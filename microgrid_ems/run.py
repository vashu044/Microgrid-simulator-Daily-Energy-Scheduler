#!/usr/bin/env python3
"""
Quick start script for Microgrid EMS
Run this to launch the Streamlit web interface.
"""

import os
import sys
import subprocess

def main():
    """Launch the Streamlit application."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the frontend app
    app_path = os.path.join(script_dir, "frontend", "app.py")
    
    # Check if app.py exists
    if not os.path.exists(app_path):
        print("❌ Error: frontend/app.py not found!")
        print(f"Looking for: {app_path}")
        sys.exit(1)
    
    print("🚀 Launching Microgrid EMS...")
    print(f"📂 Working directory: {script_dir}")
    print(f"📄 App: {app_path}")
    print("\n⚡ Starting Streamlit server...\n")
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running Streamlit: {e}")
        print("\nMake sure Streamlit is installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down EMS...")
        sys.exit(0)

if __name__ == "__main__":
    main()  