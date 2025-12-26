#!/usr/bin/env python3
"""
Guardian AI Backend Runner

Main entry point for running the Guardian AI backend services.
Initializes all components and starts the API server.
"""

import sys
import os
import logging
import asyncio
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def setup_logging():
    """Setup comprehensive logging for the application."""
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(logs_dir / "guardian_ai.log")
        ]
    )
    
    # Add error-only file handler
    error_handler = logging.FileHandler(logs_dir / "guardian_ai_error.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(error_handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("torch").setLevel(logging.WARNING)
    logging.getLogger("networkx").setLevel(logging.WARNING)

def check_dependencies():
    """Check that all required dependencies are installed."""
    
    required_packages = [
        ("torch", "PyTorch"),
        ("networkx", "NetworkX"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn")
    ]
    
    missing_packages = []
    
    for package, display_name in required_packages:
        try:
            __import__(package)
            print(f"✓ {display_name} is installed")
        except ImportError:
            missing_packages.append(display_name)
            print(f"✗ {display_name} is missing")
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    print("All dependencies are satisfied!")
    return True

def initialize_data():
    """Initialize sample data if not present."""
    
    from backend.core.data_loader import export_sample_data
    
    data_dir = Path("backend/data")
    
    # Check if data files exist
    required_files = [
        "supply_chain_data.json",
        "simulation_scenarios.json", 
        "mitigation_strategies.json"
    ]
    
    missing_files = [f for f in required_files if not (data_dir / f).exists()]
    
    if missing_files:
        print(f"Generating missing data files: {', '.join(missing_files)}")
        try:
            export_sample_data(str(data_dir), num_vendors=50)
            print("✓ Sample data generated successfully")
        except Exception as e:
            print(f"✗ Failed to generate sample data: {e}")
            return False
    else:
        print("✓ All data files are present")
    
    return True

def initialize_models():
    """Initialize GNN models if not present."""
    
    from backend.core.gnn_model import create_default_model
    
    models_dir = Path("backend/models")
    models_dir.mkdir(exist_ok=True)
    
    model_path = models_dir / "supply_chain_gnn.pth"
    
    if not model_path.exists() or model_path.stat().st_size == 0:
        print("Creating default GNN model...")
        try:
            create_default_model(str(model_path))
            print("✓ Default GNN model created")
        except Exception as e:
            print(f"⚠ Failed to create GNN model: {e}")
            print("  The system will use fallback risk calculations")
    else:
        print("✓ GNN model is present")
    
    return True

def run_server(host="0.0.0.0", port=8000, reload=False):
    """Run the FastAPI server."""
    
    import uvicorn
    from backend.api.main import app
    
    print(f"\n🚀 Starting Guardian AI Backend Server")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Reload: {reload}")
    print(f"   API Documentation: http://{host}:{port}/docs")
    print(f"   Health Check: http://{host}:{port}/health")
    print("\n" + "="*50)
    
    try:
        uvicorn.run(
            "backend.api.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server failed to start: {e}")
        sys.exit(1)

def main():
    """Main entry point."""
    
    print("🛡️  Guardian AI Backend Initialization")
    print("="*50)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check dependencies
    print("\n📦 Checking Dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # Initialize data
    print("\n📊 Initializing Data...")
    if not initialize_data():
        sys.exit(1)
    
    # Initialize models
    print("\n🧠 Initializing Models...")
    if not initialize_models():
        # Continue anyway - system can work without GNN
        pass
    
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description="Guardian AI Backend Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--dev", action="store_true", help="Development mode (enables reload)")
    
    args = parser.parse_args()
    
    # Development mode
    if args.dev:
        args.reload = True
        args.host = "127.0.0.1"
    
    # Start server
    run_server(host=args.host, port=args.port, reload=args.reload)

if __name__ == "__main__":
    main()