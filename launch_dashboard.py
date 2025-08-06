#!/usr/bin/env python3
"""
Launcher script for the trading bot dashboard
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Setup the Python path and environment"""
    # Get the current directory
    current_dir = Path(__file__).parent.absolute()
    
    # Add src directory to Python path
    src_path = current_dir / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))
        print(f"✅ Added {src_path} to Python path")
    else:
        print(f"❌ Warning: {src_path} not found")
    
    # Add current directory to Python path
    sys.path.insert(0, str(current_dir))
    print(f"✅ Added {current_dir} to Python path")

def main():
    """Main launcher function"""
    print("🚀 Launching Trading Bot Dashboard...")
    
    # Setup environment
    setup_environment()
    
    # Check if required files exist
    dashboard_file = Path("trading_dashboard.py")
    if not dashboard_file.exists():
        print(f"❌ Error: {dashboard_file} not found")
        return 1
    
    # Import and run streamlit
    try:
        import streamlit.web.cli as stcli
        import sys
        
        # Set up streamlit arguments
        sys.argv = [
            "streamlit", 
            "run", 
            str(dashboard_file),
            "--server.port", "8501",
            "--server.address", "localhost"
        ]
        
        print("🌐 Starting Streamlit server...")
        print("📊 Dashboard will be available at: http://localhost:8501")
        print("⏹️  Press Ctrl+C to stop the server")
        
        # Run streamlit
        stcli.main()
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("💡 Please install streamlit: pip install streamlit")
        return 1
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 