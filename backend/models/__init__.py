"""
Guardian AI Models Module

Pre-trained models and model management utilities for the Guardian AI platform.
"""

import os
from pathlib import Path

# Model directory
MODELS_DIR = Path(__file__).parent

def get_model_path(model_name: str) -> str:
    """Get the full path to a model file."""
    return str(MODELS_DIR / model_name)

def list_available_models() -> list:
    """List all available model files."""
    if not MODELS_DIR.exists():
        return []
    
    model_files = []
    for file in MODELS_DIR.iterdir():
        if file.suffix in ['.pth', '.pkl', '.joblib']:
            model_files.append(file.name)
    
    return model_files

def ensure_models_directory():
    """Ensure the models directory exists."""
    MODELS_DIR.mkdir(exist_ok=True)
    
    # Create placeholder for default model
    default_model_path = MODELS_DIR / "supply_chain_gnn.pth"
    if not default_model_path.exists():
        # Create empty file as placeholder
        default_model_path.touch()

# Initialize on import
ensure_models_directory()