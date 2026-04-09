"""
Startup script to run FastAPI backend on port 8001 with proper configuration.
This ensures the backend runs on the correct port for frontend connectivity.
"""

import uvicorn
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run the FastAPI backend on port 8001."""
    print("Starting EV Charging Platform Backend...")
    print("Port: 8001")
    print("Host: 127.0.0.1")
    print("CORS: Enabled for all origins")
    print("=" * 50)
    
    # Run uvicorn with the correct configuration
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
