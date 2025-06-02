#!/usr/bin/env python3
"""
Startup script for the Climate Action Intelligence Platform RAG Application.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run the Streamlit application."""
    
    # Get the directory of this script
    app_dir = Path(__file__).parent
    frontend_dir = app_dir / "frontend"
    
    # Change to the frontend directory
    os.chdir(frontend_dir)
    
    # Add backend to Python path
    backend_dir = app_dir / "backend"
    sys.path.insert(0, str(backend_dir))
    
    # Run Streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "12000",
        "--server.address", "0.0.0.0",
        "--server.allowRunOnSave", "true",
        "--server.runOnSave", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    print("Starting Climate Action Intelligence Platform RAG Application...")
    print(f"Application will be available at: http://localhost:12000")
    print("Press Ctrl+C to stop the application")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
    except subprocess.CalledProcessError as e:
        print(f"Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()