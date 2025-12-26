"""
Guardian AI Data Module

Data management, loading, and processing utilities for the Guardian AI platform.
Includes MERCOR dataset integration and synthetic data generation.
"""

import os
from pathlib import Path

# Data directory
DATA_DIR = Path(__file__).parent

def get_data_path(filename: str) -> str:
    """Get the full path to a data file."""
    return str(DATA_DIR / filename)

def ensure_data_directory():
    """Ensure the data directory exists with sample files."""
    DATA_DIR.mkdir(exist_ok=True)
    
    # Create sample data files if they don't exist
    sample_files = [
        "vendors.csv",
        "dependencies.csv", 
        "supply_chain_data.json",
        "simulation_scenarios.json",
        "mitigation_strategies.json"
    ]
    
    for filename in sample_files:
        filepath = DATA_DIR / filename
        if not filepath.exists():
            filepath.touch()

# Initialize on import
ensure_data_directory()