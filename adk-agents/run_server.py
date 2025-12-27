#!/usr/bin/env python3
"""
Run ADK Web Server on port 3000
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Run ADK web server on port 3000"""
    try:
        from google.adk.cli import main as adk_main
        
        # Set port via environment variable
        os.environ['ADK_PORT'] = '3000'
        
        # Run ADK web server
        sys.argv = ['adk', 'web', '--port', '3000']
        adk_main()
    except ImportError:
        print("Error: google-adk not installed")
        print("Install it with: pip install google-adk")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()





