"""
Guardian AI Performance Optimization Module

Performance monitoring, optimization, and caching utilities for the Guardian AI platform.
"""

import time
import functools
import logging
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from collections import defaultdict, deque
import threading
import psutil
import gc
from datetime import datetime, timedelta
import json
import pickle
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    memory_available: float
    active_threads: int
    cache_hit_rate: float
    average_response_time: float
    operations_per_second: float

class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str = "operation"):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        self.duration = self.end_time - self.start_time
        logger.debug(f"{self.operation_name} completed in {self.duration:.4f} seconds")

def performance_monitor(func):
    """Decorator to monitor function performance."""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            result = None
            success = False
            raise
        finally:
            end_time = time.perf_counter()
            duration = end_time - start_time
            
            # Log performance metrics
            status = "SUCCESS" if success else "FAILED"
            logger.debug(f"PERF [{status}] {func.__name__}: {duration:.4f}s")
            
            # Store in performance tracker if available
            if hasattr(wrapper, '_performance_tracker'):
                wrapper._performance_tracker.record_operation(
                    func.__name__, duration, success
                )
        
        return result
    
    return wrapper

class PerformanceTracker:
    """Track and analyze performance metrics across the system."""
    
    def __init__(self, max_history: int = 10000):
        self.max_history = max_history
        self.operation_history = defaultdict(lambda: deque(maxlen=max_history))
        self.system_metrics = deque(maxlen=1440)  # 24 hours at 1-minute intervals
        self.lock = threading.Lock()
        
        # Performance counters
        self.operation_counts = defaultdict(int)
        self.operation_total_time = defaultdict(float)
        self.operation_errors = defaultdict(int)
        
        # Start system monitoring
        self.monitoring_active = False
        self.monitoring_thread = None
    
    def record_operation(self, operation_name: str, duration: float, success: bool = True):
        """Record an operation's performance."""
        
        with self.lock:
            timestamp = datetime.now()
            
            self.operation_history[operation_name].append({
                'timestamp': timestamp,
                'duration': duration,
                'success': success
            })
            
            self.operation_counts[operation_name] += 1
            self.operation_total_time[operation_name] += duration
            
            if not success:
                self.operation_errors[operation_name] += 1
    
    def get_operation_stats(self, operation_name: str) -> Dict[str, Any]:
        """Get statistics for a specific operation."""
        
        with self.lock:
            history = list(self.operation_history[operation_name])
            
            if not history:
                return {
                    'operation': operation_name,
                    'total_calls': 0,
                    'average_duration': 0.0,
                    'min_duration': 0.0,
                    'max_duration': 0.0,
                    'success_rate': 0.0,
                    'calls_per_minute': 0.0
                }
            
            durations = [h['duration'] for h in history]
            successes = [h['success'] for h in history]
            
            # Calculate time-based metrics
            now = datetime.now()
            recent_history = [h for h in history if (now - h['timestamp']).total_seconds() <= 3600]  # Last hour
            
            return {
                'operation': operation_name,
                'total_calls': len(history),
                'average_duration': sum(durations) / len(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'success_rate': sum(successes) / len(successes),
                'calls_per_minute': len(recent_history) / 60.0,
                'error_count': self.operation_errors[operation_name],
                'total_time': self.operation_total_time[operation_name]
            }
    
    def get_all_operation_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all tracked operations."""
        
        stats = []
        for operation_name in self.operation_history.keys():
            stats.append(self.get_operation_stats(operation_name))
        
        return sorted(stats, key=lambda x: x['total_calls'], reverse=True)
    
    def start_system_monitoring(self, interval: int = 60):
        """Start monitoring system performance metrics."""
        
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._system_monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitoring_thread.start()
        
        logger.info("System performance monitoring started")
    
    def stop_system_monitoring(self):
        """Stop system performance monitoring."""
        
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("System performance monitoring stopped")
    
    def _system_monitoring_loop(self, interval: int):
        """System monitoring loop."""
        
        while self.monitoring_active:
            try:
                metrics = self._collect_system_metrics()
                self.system_metrics.append(metrics)
            except Exception as e:
                logger.error(f"System metrics collection failed: {e}")
            
            time.sleep(interval)
    
    def _collect_system_metrics(self) -> PerformanceMetrics:
        """Collect current system performance metrics."""
        
        # CPU and memory usage
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        memory_available = memory.available / (1024 * 1024 * 1024)  # GB
        
        # Thread count
        active_threads = threading.active_count()
        
        # Calculate cache hit rate (if cache is available)
        cache_hit_rate = 0.0
        if hasattr(self, '_cache_stats'):
            cache_hit_rate = self._cache_stats.get('hit_rate', 0.0)
        
        # Calculate average response time from recent operations
        average_response_time = 0.0
        total_operations = 0
        total_time = 0.0
        
        now = datetime.now()
        cutoff = now - timedelta(minutes=5)  # Last 5 minutes
        
        for operation_history in self.operation_history.values():
            recent_ops = [op for op in operation_history if op['timestamp'] >= cutoff]
            if recent_ops:
                total_operations += len(recent_ops)
                total_time += sum(op['duration'] for op in recent_ops)
        
        if total_operations > 0:
            average_response_time = total_time / total_operations
        
        # Operations per second
        operations_per_second = total_operations / 300.0 if total_operations > 0 else 0.0  # 5 minutes = 300 seconds
        
        return PerformanceMetrics(
            timestamp=now,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            memory_available=memory_available,
            active_threads=active_threads,
            cache_hit_rate=cache_hit_rate,
            average_response_time=average_response_time,
            operations_per_second=operations_per_second
        )
    
    def get_system_health_score(self) -> float:
        """Calculate overall system health score (0-1)."""
        
        if not self.system_metrics:
            return 0.5  # Unknown
        
        latest_metrics = self.system_metrics[-1]
        
        # Health factors (lower is better for CPU/memory, higher is better for others)
        cpu_health = max(0, 1 - (latest_metrics.cpu_usage / 100))
        memory_health = max(0, 1 - (latest_metrics.memory_usage / 100))
        response_time_health = max(0, 1 - min(1, latest_metrics.average_response_time / 5.0))  # 5s max
        cache_health = latest_metrics.cache_hit_rate
        
        # Weighted average
        health_score = (
            cpu_health * 0.25 +
            memory_health * 0.25 +
            response_time_health * 0.3 +
            cache_health * 0.2
        )
        
        return health_score
    
    def export_performance_report(self, output_path: str):
        """Export comprehensive performance report."""
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'system_health_score': self.get_system_health_score(),
            'operation_statistics': self.get_all_operation_stats(),
            'system_metrics': [
                {
                    'timestamp': m.timestamp.isoformat(),
                    'cpu_usage': m.cpu_usage,
                    'memory_usage': m.memory_usage,
                    'memory_available': m.memory_available,
                    'active_threads': m.active_threads,
                    'cache_hit_rate': m.cache_hit_rate,
                    'average_response_time': m.average_response_time,
                    'operations_per_second': m.operations_per_second
                }
                for m in list(self.system_metrics)[-100:]  # Last 100 data points
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"Performance report exported to {output_path}")

class InMemoryCache:
    """High-performance in-memory cache with TTL support."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = {}
        self.access_times = {}
        self.expiry_times = {}
        self.lock = threading.RLock()
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def _generate_key(self, key: Any) -> str:
        """Generate a string key from any hashable object."""
        if isinstance(key, str):
            return key
        
        # Create hash of the key
        key_str = str(key)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _is_expired(self, key: str) -> bool:
        """Check if a cache entry has expired."""
        if key not in self.expiry_times:
            return True
        
        return datetime.now() > self.expiry_times[key]
    
    def _evict_expired(self):
        """Remove expired entries."""
        now = datetime.now()
        expired_keys = [
            key for key, expiry in self.expiry_times.items()
            if now > expiry
        ]
        
        for key in expired_keys:
            self._remove_key(key)
    
    def _evict_lru(self):
        """Evict least recently used entries to make space."""
        if len(self.cache) <= self.max_size:
            return
        
        # Sort by access time and remove oldest
        sorted_keys = sorted(
            self.access_times.items(),
            key=lambda x: x[1]
        )
        
        keys_to_remove = sorted_keys[:len(self.cache) - self.max_size + 1]
        
        for key, _ in keys_to_remove:
            self._remove_key(key)
            self.evictions += 1
    
    def _remove_key(self, key: str):
        """Remove a key from all cache structures."""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
        self.expiry_times.pop(key, None)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get a value from the cache."""
        
        with self.lock:
            str_key = self._generate_key(key)
            
            # Check if key exists and is not expired
            if str_key in self.cache and not self._is_expired(str_key):
                self.access_times[str_key] = datetime.now()
                self.hits += 1
                return self.cache[str_key]
            
            # Cache miss
            self.misses += 1
            
            # Remove expired entry if it exists
            if str_key in self.cache:
                self._remove_key(str_key)
            
            return default
    
    def set(self, key: Any, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in the cache."""
        
        with self.lock:
            str_key = self._generate_key(key)
            
            # Clean up expired entries
            self._evict_expired()
            
            # Set the value
            self.cache[str_key] = value
            self.access_times[str_key] = datetime.now()
            
            # Set expiry time
            ttl = ttl or self.default_ttl
            self.expiry_times[str_key] = datetime.now() + timedelta(seconds=ttl)
            
            # Evict LRU if necessary
            self._evict_lru()
    
    def delete(self, key: Any) -> bool:
        """Delete a key from the cache."""
        
        with self.lock:
            str_key = self._generate_key(key)
            
            if str_key in self.cache:
                self._remove_key(str_key)
                return True
            
            return False
    
    def clear(self):
        """Clear all cache entries."""
        
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            self.expiry_times.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0.0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': hit_rate,
                'evictions': self.evictions,
                'memory_usage_mb': self._estimate_memory_usage()
            }
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB."""
        try:
            import sys
            total_size = 0
            
            for key, value in self.cache.items():
                total_size += sys.getsizeof(key) + sys.getsizeof(value)
            
            return total_size / (1024 * 1024)  # Convert to MB
        except:
            return 0.0

def cached(ttl: int = 3600, cache_instance: Optional[InMemoryCache] = None):
    """Decorator to cache function results."""
    
    def decorator(func):
        # Use provided cache or create a default one
        cache = cache_instance or InMemoryCache(default_ttl=ttl)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        # Attach cache instance for external access
        wrapper._cache = cache
        return wrapper
    
    return decorator

class BatchProcessor:
    """Process operations in batches for better performance."""
    
    def __init__(self, batch_size: int = 100, flush_interval: int = 5):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batches = defaultdict(list)
        self.processors = {}
        self.lock = threading.Lock()
        self.last_flush = datetime.now()
        
        # Start flush timer
        self.flush_timer = threading.Timer(flush_interval, self._flush_all_batches)
        self.flush_timer.daemon = True
        self.flush_timer.start()
    
    def register_processor(self, batch_type: str, processor_func: Callable[[List], None]):
        """Register a batch processor function."""
        self.processors[batch_type] = processor_func
    
    def add_to_batch(self, batch_type: str, item: Any):
        """Add an item to a batch."""
        
        with self.lock:
            self.batches[batch_type].append(item)
            
            # Flush if batch is full
            if len(self.batches[batch_type]) >= self.batch_size:
                self._flush_batch(batch_type)
    
    def _flush_batch(self, batch_type: str):
        """Flush a specific batch."""
        
        if batch_type not in self.batches or not self.batches[batch_type]:
            return
        
        if batch_type not in self.processors:
            logger.warning(f"No processor registered for batch type: {batch_type}")
            return
        
        batch_items = self.batches[batch_type].copy()
        self.batches[batch_type].clear()
        
        try:
            self.processors[batch_type](batch_items)
            logger.debug(f"Processed batch of {len(batch_items)} items for {batch_type}")
        except Exception as e:
            logger.error(f"Batch processing failed for {batch_type}: {e}")
    
    def _flush_all_batches(self):
        """Flush all batches."""
        
        with self.lock:
            for batch_type in list(self.batches.keys()):
                self._flush_batch(batch_type)
        
        self.last_flush = datetime.now()
        
        # Schedule next flush
        self.flush_timer = threading.Timer(self.flush_interval, self._flush_all_batches)
        self.flush_timer.daemon = True
        self.flush_timer.start()
    
    def force_flush(self, batch_type: Optional[str] = None):
        """Force flush batches immediately."""
        
        with self.lock:
            if batch_type:
                self._flush_batch(batch_type)
            else:
                self._flush_all_batches()

class MemoryOptimizer:
    """Utilities for memory optimization."""
    
    @staticmethod
    def force_garbage_collection():
        """Force garbage collection and return memory stats."""
        
        # Get memory before GC
        process = psutil.Process()
        memory_before = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Force garbage collection
        collected = gc.collect()
        
        # Get memory after GC
        memory_after = process.memory_info().rss / (1024 * 1024)  # MB
        memory_freed = memory_before - memory_after
        
        logger.info(f"Garbage collection: {collected} objects collected, {memory_freed:.2f} MB freed")
        
        return {
            'objects_collected': collected,
            'memory_before_mb': memory_before,
            'memory_after_mb': memory_after,
            'memory_freed_mb': memory_freed
        }
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Get current memory usage statistics."""
        
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / (1024 * 1024),
            'vms_mb': memory_info.vms / (1024 * 1024),
            'percent': process.memory_percent(),
            'available_mb': psutil.virtual_memory().available / (1024 * 1024)
        }
    
    @staticmethod
    def optimize_dataframe(df) -> Any:
        """Optimize pandas DataFrame memory usage."""
        
        try:
            import pandas as pd
            
            if not isinstance(df, pd.DataFrame):
                return df
            
            # Optimize numeric columns
            for col in df.select_dtypes(include=['int64']).columns:
                df[col] = pd.to_numeric(df[col], downcast='integer')
            
            for col in df.select_dtypes(include=['float64']).columns:
                df[col] = pd.to_numeric(df[col], downcast='float')
            
            # Optimize object columns
            for col in df.select_dtypes(include=['object']).columns:
                if df[col].nunique() / len(df) < 0.5:  # Less than 50% unique values
                    df[col] = df[col].astype('category')
            
            return df
            
        except ImportError:
            return df

# Global performance tracker instance
global_performance_tracker = PerformanceTracker()

# Global cache instance
global_cache = InMemoryCache(max_size=5000, default_ttl=1800)  # 30 minutes default TTL

def get_performance_tracker() -> PerformanceTracker:
    """Get the global performance tracker instance."""
    return global_performance_tracker

def get_global_cache() -> InMemoryCache:
    """Get the global cache instance."""
    return global_cache

def optimize_system_performance():
    """Run system performance optimizations."""
    
    logger.info("Running system performance optimizations...")
    
    # Force garbage collection
    gc_stats = MemoryOptimizer.force_garbage_collection()
    
    # Clear expired cache entries
    global_cache._evict_expired()
    
    # Get current performance metrics
    memory_stats = MemoryOptimizer.get_memory_usage()
    cache_stats = global_cache.get_stats()
    
    logger.info(f"Performance optimization completed:")
    logger.info(f"  Memory usage: {memory_stats['rss_mb']:.1f} MB")
    logger.info(f"  Cache hit rate: {cache_stats['hit_rate']:.2%}")
    logger.info(f"  Objects collected: {gc_stats['objects_collected']}")
    
    return {
        'memory_stats': memory_stats,
        'cache_stats': cache_stats,
        'gc_stats': gc_stats
    }