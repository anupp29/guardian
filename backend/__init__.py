"""
Guardian AI Backend Package

Enterprise-grade supply chain risk intelligence platform backend.
Combines Graph Neural Networks, advanced simulation, and AI agent orchestration
for comprehensive supply chain security analysis.

Key Features:
- Graph Neural Network-based structural risk learning
- Advanced cascade failure simulation
- Real-time risk assessment and monitoring
- AI-powered mitigation strategy generation
- Comprehensive supply chain visualization
- Enterprise-ready scalability and performance

Architecture:
- Core: Graph processing, GNN models, risk calculation
- Agents: AI agent orchestration for reasoning and analysis
- API: RESTful services for frontend integration
- Data: MERCOR dataset integration and synthetic data generation
"""

from .core import *

__version__ = "1.0.0"
__author__ = "Guardian AI Team"
__description__ = "Supply Chain Risk Intelligence Platform Backend"

# Package metadata
__package_info__ = {
    'name': 'guardian-ai-backend',
    'version': __version__,
    'description': __description__,
    'author': __author__,
    'license': 'MIT',
    'python_requires': '>=3.8',
    'dependencies': [
        'torch>=1.12.0',
        'torch-geometric>=2.1.0',
        'networkx>=2.8',
        'numpy>=1.21.0',
        'pandas>=1.4.0',
        'scikit-learn>=1.1.0',
        'matplotlib>=3.5.0',
        'seaborn>=0.11.0',
        'fastapi>=0.85.0',
        'uvicorn>=0.18.0',
        'pydantic>=1.10.0',
        'python-multipart>=0.0.5'
    ]
}

# System configuration
DEFAULT_CONFIG = {
    'gnn': {
        'model_path': 'models/supply_chain_gnn.pth',
        'input_dim': 16,
        'hidden_dim': 64,
        'output_dim': 32,
        'num_layers': 3,
        'dropout': 0.2,
        'use_sage': True
    },
    'simulation': {
        'max_steps': 20,
        'max_time_ms': 10000,
        'base_propagation_probability': 0.3,
        'base_propagation_delay': 300
    },
    'risk': {
        'risk_threshold': 0.6,
        'tier_multipliers': {1: 3.0, 2: 2.0, 3: 1.0},
        'update_interval_minutes': 15
    },
    'data': {
        'default_vendors': 50,
        'cache_ttl_hours': 24,
        'export_formats': ['json', 'csv', 'cytoscape']
    }
}

def get_version():
    """Get the current version of Guardian AI Backend."""
    return __version__

def get_system_info():
    """Get comprehensive system information."""
    import sys
    import platform
    
    try:
        import torch
        torch_version = torch.__version__
        cuda_available = torch.cuda.is_available()
    except ImportError:
        torch_version = "Not installed"
        cuda_available = False
    
    try:
        import networkx as nx
        networkx_version = nx.__version__
    except ImportError:
        networkx_version = "Not installed"
    
    return {
        'guardian_ai_version': __version__,
        'python_version': sys.version,
        'platform': platform.platform(),
        'torch_version': torch_version,
        'cuda_available': cuda_available,
        'networkx_version': networkx_version,
        'architecture': platform.architecture()[0]
    }

def validate_environment():
    """Validate that the environment has all required dependencies."""
    
    required_packages = [
        'torch',
        'networkx', 
        'numpy',
        'pandas'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        raise ImportError(
            f"Missing required packages: {', '.join(missing_packages)}. "
            f"Please install them using: pip install {' '.join(missing_packages)}"
        )
    
    return True

# Initialize logging
import logging

def setup_logging(level=logging.INFO, format_string=None):
    """Setup logging configuration for Guardian AI."""
    
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('guardian_ai.log')
        ]
    )
    
    # Set specific loggers
    logging.getLogger('guardian_ai').setLevel(level)
    logging.getLogger('torch').setLevel(logging.WARNING)
    logging.getLogger('networkx').setLevel(logging.WARNING)

# Auto-setup logging on import
setup_logging()

logger = logging.getLogger(__name__)
logger.info(f"Guardian AI Backend v{__version__} initialized")

# Validate environment on import
try:
    validate_environment()
    logger.info("Environment validation successful")
except ImportError as e:
    logger.error(f"Environment validation failed: {e}")
    raise