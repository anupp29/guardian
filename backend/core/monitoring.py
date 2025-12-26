"""
Guardian AI Monitoring Module

Real-time monitoring and alerting system for supply chain risk changes.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import json
import threading
import time
from collections import deque, defaultdict

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    RISK_INCREASE = "risk_increase"
    NEW_VULNERABILITY = "new_vulnerability"
    VENDOR_STATUS_CHANGE = "vendor_status_change"
    SIMULATION_ANOMALY = "simulation_anomaly"
    THRESHOLD_BREACH = "threshold_breach"
    SYSTEM_HEALTH = "system_health"

@dataclass
class Alert:
    id: str
    timestamp: datetime
    severity: AlertSeverity
    alert_type: AlertType
    title: str
    description: str
    affected_entities: List[str]
    metadata: Dict[str, Any]
    acknowledged: bool = False
    resolved: bool = False

@dataclass
class MonitoringMetrics:
    timestamp: datetime
    overall_risk_score: float
    tier_1_exposure: float
    cascade_potential: float
    vulnerability_density: float
    resilience_score: float
    active_alerts: int
    system_health: float

class RiskThresholds:
    """Configurable risk thresholds for monitoring."""
    
    def __init__(self):
        self.overall_risk_critical = 0.8
        self.overall_risk_high = 0.6
        self.overall_risk_warning = 0.4
        
        self.tier_1_exposure_critical = 0.7
        self.tier_1_exposure_high = 0.5
        
        self.cascade_potential_critical = 0.8
        self.cascade_potential_high = 0.6
        
        self.vulnerability_density_critical = 0.3
        self.vulnerability_density_high = 0.2
        
        self.resilience_score_critical = 0.3
        self.resilience_score_warning = 0.5

class SupplyChainMonitor:
    """Real-time monitoring system for supply chain risk."""
    
    def __init__(self, supply_chain_graph, risk_calculator=None, simulation_engine=None):
        self.graph = supply_chain_graph
        self.risk_calculator = risk_calculator
        self.simulation_engine = simulation_engine
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_thread = None
        self.monitoring_interval = 60  # seconds
        
        # Alert management
        self.alerts = deque(maxlen=1000)  # Keep last 1000 alerts
        self.alert_handlers = []
        self.thresholds = RiskThresholds()
        
        # Metrics history
        self.metrics_history = deque(maxlen=1440)  # 24 hours at 1-minute intervals
        
        # Previous state for change detection
        self.previous_metrics = None
        self.previous_node_risks = {}
        
        # Alert ID counter
        self.alert_counter = 0
    
    def start_monitoring(self):
        """Start the monitoring system."""
        if self.is_monitoring:
            logger.warning("Monitoring is already running")
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("Supply chain monitoring started")
        self._create_alert(
            AlertSeverity.INFO,
            AlertType.SYSTEM_HEALTH,
            "Monitoring Started",
            "Supply chain monitoring system has been activated",
            []
        )
    
    def stop_monitoring(self):
        """Stop the monitoring system."""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Supply chain monitoring stopped")
        self._create_alert(
            AlertSeverity.INFO,
            AlertType.SYSTEM_HEALTH,
            "Monitoring Stopped",
            "Supply chain monitoring system has been deactivated",
            []
        )
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                self._perform_monitoring_cycle()
            except Exception as e:
                logger.error(f"Monitoring cycle failed: {e}")
                self._create_alert(
                    AlertSeverity.HIGH,
                    AlertType.SYSTEM_HEALTH,
                    "Monitoring Error",
                    f"Monitoring cycle encountered an error: {str(e)}",
                    []
                )
            
            time.sleep(self.monitoring_interval)
    
    def _perform_monitoring_cycle(self):
        """Perform a single monitoring cycle."""
        current_time = datetime.now()
        
        # Calculate current metrics
        current_metrics = self._calculate_current_metrics(current_time)
        
        # Store metrics history
        self.metrics_history.append(current_metrics)
        
        # Check for threshold breaches
        self._check_threshold_breaches(current_metrics)
        
        # Check for significant changes
        if self.previous_metrics:
            self._check_metric_changes(current_metrics, self.previous_metrics)
        
        # Check individual node risk changes
        if self.risk_calculator:
            self._check_node_risk_changes()
        
        # Update previous state
        self.previous_metrics = current_metrics
        
        logger.debug(f"Monitoring cycle completed at {current_time}")
    
    def _calculate_current_metrics(self, timestamp: datetime) -> MonitoringMetrics:
        """Calculate current monitoring metrics."""
        
        # Default values
        overall_risk_score = 0.0
        tier_1_exposure = 0.0
        cascade_potential = 0.0
        vulnerability_density = 0.0
        resilience_score = 1.0
        
        # Calculate risk metrics if calculator available
        if self.risk_calculator:
            try:
                risk_metrics = self.risk_calculator.calculate_comprehensive_risk(self.graph)
                overall_risk_score = risk_metrics.overall_score
                tier_1_exposure = risk_metrics.tier_1_exposure
                cascade_potential = risk_metrics.cascade_potential
                vulnerability_density = risk_metrics.vulnerability_density
                resilience_score = risk_metrics.resilience_score
            except Exception as e:
                logger.error(f"Risk calculation failed in monitoring: {e}")
        
        # Count active alerts
        active_alerts = len([a for a in self.alerts if not a.resolved])
        
        # Calculate system health (simplified)
        system_health = min(1.0, resilience_score * (1.0 - overall_risk_score))
        
        return MonitoringMetrics(
            timestamp=timestamp,
            overall_risk_score=overall_risk_score,
            tier_1_exposure=tier_1_exposure,
            cascade_potential=cascade_potential,
            vulnerability_density=vulnerability_density,
            resilience_score=resilience_score,
            active_alerts=active_alerts,
            system_health=system_health
        )
    
    def _check_threshold_breaches(self, metrics: MonitoringMetrics):
        """Check for threshold breaches and create alerts."""
        
        # Overall risk score thresholds
        if metrics.overall_risk_score >= self.thresholds.overall_risk_critical:
            self._create_alert(
                AlertSeverity.CRITICAL,
                AlertType.THRESHOLD_BREACH,
                "Critical Risk Level Reached",
                f"Overall risk score ({metrics.overall_risk_score:.3f}) has reached critical threshold",
                []
            )
        elif metrics.overall_risk_score >= self.thresholds.overall_risk_high:
            self._create_alert(
                AlertSeverity.HIGH,
                AlertType.THRESHOLD_BREACH,
                "High Risk Level Detected",
                f"Overall risk score ({metrics.overall_risk_score:.3f}) has reached high threshold",
                []
            )
        elif metrics.overall_risk_score >= self.thresholds.overall_risk_warning:
            self._create_alert(
                AlertSeverity.WARNING,
                AlertType.THRESHOLD_BREACH,
                "Elevated Risk Level",
                f"Overall risk score ({metrics.overall_risk_score:.3f}) has reached warning threshold",
                []
            )
        
        # Tier 1 exposure thresholds
        if metrics.tier_1_exposure >= self.thresholds.tier_1_exposure_critical:
            self._create_alert(
                AlertSeverity.CRITICAL,
                AlertType.THRESHOLD_BREACH,
                "Critical Tier 1 Exposure",
                f"Tier 1 vendor exposure ({metrics.tier_1_exposure:.3f}) is critically high",
                []
            )
        elif metrics.tier_1_exposure >= self.thresholds.tier_1_exposure_high:
            self._create_alert(
                AlertSeverity.HIGH,
                AlertType.THRESHOLD_BREACH,
                "High Tier 1 Exposure",
                f"Tier 1 vendor exposure ({metrics.tier_1_exposure:.3f}) is elevated",
                []
            )
        
        # Cascade potential thresholds
        if metrics.cascade_potential >= self.thresholds.cascade_potential_critical:
            self._create_alert(
                AlertSeverity.CRITICAL,
                AlertType.THRESHOLD_BREACH,
                "Critical Cascade Risk",
                f"Cascade potential ({metrics.cascade_potential:.3f}) is critically high",
                []
            )
        elif metrics.cascade_potential >= self.thresholds.cascade_potential_high:
            self._create_alert(
                AlertSeverity.HIGH,
                AlertType.THRESHOLD_BREACH,
                "High Cascade Risk",
                f"Cascade potential ({metrics.cascade_potential:.3f}) is elevated",
                []
            )
        
        # Resilience score thresholds (lower is worse)
        if metrics.resilience_score <= self.thresholds.resilience_score_critical:
            self._create_alert(
                AlertSeverity.CRITICAL,
                AlertType.THRESHOLD_BREACH,
                "Critical Resilience Degradation",
                f"System resilience ({metrics.resilience_score:.3f}) is critically low",
                []
            )
        elif metrics.resilience_score <= self.thresholds.resilience_score_warning:
            self._create_alert(
                AlertSeverity.WARNING,
                AlertType.THRESHOLD_BREACH,
                "Resilience Degradation",
                f"System resilience ({metrics.resilience_score:.3f}) is below optimal levels",
                []
            )
    
    def _check_metric_changes(self, current: MonitoringMetrics, previous: MonitoringMetrics):
        """Check for significant changes in metrics."""
        
        # Define significant change thresholds
        risk_change_threshold = 0.1
        exposure_change_threshold = 0.15
        cascade_change_threshold = 0.1
        resilience_change_threshold = 0.1
        
        # Check overall risk score changes
        risk_change = current.overall_risk_score - previous.overall_risk_score
        if abs(risk_change) >= risk_change_threshold:
            severity = AlertSeverity.HIGH if abs(risk_change) >= 0.2 else AlertSeverity.WARNING
            direction = "increased" if risk_change > 0 else "decreased"
            
            self._create_alert(
                severity,
                AlertType.RISK_INCREASE if risk_change > 0 else AlertType.SYSTEM_HEALTH,
                f"Significant Risk Score Change",
                f"Overall risk score has {direction} by {abs(risk_change):.3f} ({previous.overall_risk_score:.3f} → {current.overall_risk_score:.3f})",
                []
            )
        
        # Check tier 1 exposure changes
        exposure_change = current.tier_1_exposure - previous.tier_1_exposure
        if abs(exposure_change) >= exposure_change_threshold:
            severity = AlertSeverity.HIGH if abs(exposure_change) >= 0.25 else AlertSeverity.WARNING
            direction = "increased" if exposure_change > 0 else "decreased"
            
            self._create_alert(
                severity,
                AlertType.RISK_INCREASE if exposure_change > 0 else AlertType.SYSTEM_HEALTH,
                f"Tier 1 Exposure Change",
                f"Critical vendor exposure has {direction} by {abs(exposure_change):.3f}",
                []
            )
        
        # Check resilience changes
        resilience_change = current.resilience_score - previous.resilience_score
        if abs(resilience_change) >= resilience_change_threshold:
            severity = AlertSeverity.HIGH if abs(resilience_change) >= 0.2 else AlertSeverity.WARNING
            direction = "improved" if resilience_change > 0 else "degraded"
            
            self._create_alert(
                severity,
                AlertType.SYSTEM_HEALTH,
                f"System Resilience Change",
                f"System resilience has {direction} by {abs(resilience_change):.3f}",
                []
            )
    
    def _check_node_risk_changes(self):
        """Check for significant changes in individual node risks."""
        
        if not self.risk_calculator:
            return
        
        try:
            current_node_risks = self.risk_calculator.calculate_node_risk_profiles(self.graph)
            
            # Compare with previous risks
            for node_id, current_profile in current_node_risks.items():
                if node_id in self.previous_node_risks:
                    previous_profile = self.previous_node_risks[node_id]
                    risk_change = current_profile.combined_risk - previous_profile.combined_risk
                    
                    # Check for significant risk increases
                    if risk_change >= 0.2:  # 20% increase
                        node_name = self.graph.graph.nodes.get(node_id, {}).get('name', node_id)
                        
                        self._create_alert(
                            AlertSeverity.HIGH,
                            AlertType.RISK_INCREASE,
                            f"Vendor Risk Increase: {node_name}",
                            f"Risk score increased by {risk_change:.3f} ({previous_profile.combined_risk:.3f} → {current_profile.combined_risk:.3f})",
                            [node_id]
                        )
                    
                    # Check for risk level changes
                    if current_profile.risk_level != previous_profile.risk_level:
                        node_name = self.graph.graph.nodes.get(node_id, {}).get('name', node_id)
                        
                        severity = AlertSeverity.HIGH if current_profile.risk_level.value in ['high', 'critical'] else AlertSeverity.WARNING
                        
                        self._create_alert(
                            severity,
                            AlertType.RISK_INCREASE,
                            f"Vendor Risk Level Change: {node_name}",
                            f"Risk level changed from {previous_profile.risk_level.value} to {current_profile.risk_level.value}",
                            [node_id]
                        )
            
            # Update previous node risks
            self.previous_node_risks = current_node_risks
            
        except Exception as e:
            logger.error(f"Node risk change detection failed: {e}")
    
    def _create_alert(self, severity: AlertSeverity, alert_type: AlertType, 
                     title: str, description: str, affected_entities: List[str],
                     metadata: Optional[Dict[str, Any]] = None):
        """Create a new alert."""
        
        self.alert_counter += 1
        alert_id = f"alert_{self.alert_counter:06d}"
        
        alert = Alert(
            id=alert_id,
            timestamp=datetime.now(),
            severity=severity,
            alert_type=alert_type,
            title=title,
            description=description,
            affected_entities=affected_entities,
            metadata=metadata or {}
        )
        
        self.alerts.append(alert)
        
        # Notify alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
        
        logger.info(f"Alert created: {severity.value.upper()} - {title}")
    
    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """Add an alert handler function."""
        self.alert_handlers.append(handler)
    
    def remove_alert_handler(self, handler: Callable[[Alert], None]):
        """Remove an alert handler function."""
        if handler in self.alert_handlers:
            self.alert_handlers.remove(handler)
    
    def get_active_alerts(self, severity_filter: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get active (unresolved) alerts."""
        active_alerts = [a for a in self.alerts if not a.resolved]
        
        if severity_filter:
            active_alerts = [a for a in active_alerts if a.severity == severity_filter]
        
        return sorted(active_alerts, key=lambda x: x.timestamp, reverse=True)
    
    def get_recent_alerts(self, hours: int = 24) -> List[Alert]:
        """Get alerts from the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [a for a in self.alerts if a.timestamp >= cutoff_time]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                logger.info(f"Alert acknowledged: {alert_id}")
                return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.acknowledged = True
                logger.info(f"Alert resolved: {alert_id}")
                return True
        return False
    
    def get_metrics_history(self, hours: int = 24) -> List[MonitoringMetrics]:
        """Get metrics history for the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [m for m in self.metrics_history if m.timestamp >= cutoff_time]
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current monitoring status."""
        
        current_metrics = self.metrics_history[-1] if self.metrics_history else None
        active_alerts = self.get_active_alerts()
        
        # Count alerts by severity
        alert_counts = defaultdict(int)
        for alert in active_alerts:
            alert_counts[alert.severity.value] += 1
        
        return {
            'monitoring_active': self.is_monitoring,
            'monitoring_interval': self.monitoring_interval,
            'last_update': current_metrics.timestamp.isoformat() if current_metrics else None,
            'current_metrics': asdict(current_metrics) if current_metrics else None,
            'active_alerts': len(active_alerts),
            'alert_counts': dict(alert_counts),
            'system_health': current_metrics.system_health if current_metrics else 0.0
        }
    
    def export_monitoring_data(self, output_path: str, hours: int = 24):
        """Export monitoring data to JSON file."""
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'monitoring_status': self.get_current_status(),
            'metrics_history': [asdict(m) for m in self.get_metrics_history(hours)],
            'recent_alerts': [asdict(a) for a in self.get_recent_alerts(hours)],
            'thresholds': {
                'overall_risk_critical': self.thresholds.overall_risk_critical,
                'overall_risk_high': self.thresholds.overall_risk_high,
                'overall_risk_warning': self.thresholds.overall_risk_warning,
                'tier_1_exposure_critical': self.thresholds.tier_1_exposure_critical,
                'tier_1_exposure_high': self.thresholds.tier_1_exposure_high,
                'cascade_potential_critical': self.thresholds.cascade_potential_critical,
                'cascade_potential_high': self.thresholds.cascade_potential_high,
                'resilience_score_critical': self.thresholds.resilience_score_critical,
                'resilience_score_warning': self.thresholds.resilience_score_warning
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"Monitoring data exported to {output_path}")


class AlertNotificationSystem:
    """System for sending alert notifications via various channels."""
    
    def __init__(self):
        self.notification_channels = []
    
    def add_email_channel(self, smtp_config: Dict[str, Any], recipients: List[str]):
        """Add email notification channel."""
        # Implementation would depend on email service
        pass
    
    def add_webhook_channel(self, webhook_url: str, headers: Optional[Dict[str, str]] = None):
        """Add webhook notification channel."""
        # Implementation would send HTTP POST to webhook
        pass
    
    def add_slack_channel(self, webhook_url: str):
        """Add Slack notification channel."""
        # Implementation would send to Slack webhook
        pass
    
    def send_notification(self, alert: Alert):
        """Send notification for an alert."""
        # Implementation would send via all configured channels
        pass


# Utility functions for monitoring setup
def create_monitoring_system(supply_chain_graph, risk_calculator=None, simulation_engine=None) -> SupplyChainMonitor:
    """Create and configure a monitoring system."""
    
    monitor = SupplyChainMonitor(supply_chain_graph, risk_calculator, simulation_engine)
    
    # Add default alert handler (logging)
    def log_alert_handler(alert: Alert):
        logger.info(f"ALERT [{alert.severity.value.upper()}] {alert.title}: {alert.description}")
    
    monitor.add_alert_handler(log_alert_handler)
    
    return monitor


def setup_monitoring_dashboard_data(monitor: SupplyChainMonitor) -> Dict[str, Any]:
    """Prepare monitoring data for dashboard display."""
    
    status = monitor.get_current_status()
    recent_alerts = monitor.get_recent_alerts(24)
    metrics_history = monitor.get_metrics_history(24)
    
    # Prepare time series data
    time_series = []
    for metrics in metrics_history[-100:]:  # Last 100 data points
        time_series.append({
            'timestamp': metrics.timestamp.isoformat(),
            'overall_risk': metrics.overall_risk_score,
            'tier_1_exposure': metrics.tier_1_exposure,
            'cascade_potential': metrics.cascade_potential,
            'resilience_score': metrics.resilience_score,
            'system_health': metrics.system_health
        })
    
    # Prepare alert summary
    alert_summary = []
    for alert in recent_alerts[:10]:  # Last 10 alerts
        alert_summary.append({
            'id': alert.id,
            'timestamp': alert.timestamp.isoformat(),
            'severity': alert.severity.value,
            'type': alert.alert_type.value,
            'title': alert.title,
            'description': alert.description,
            'acknowledged': alert.acknowledged,
            'resolved': alert.resolved
        })
    
    return {
        'status': status,
        'time_series': time_series,
        'recent_alerts': alert_summary,
        'alert_counts': status.get('alert_counts', {}),
        'system_health': status.get('system_health', 0.0)
    }