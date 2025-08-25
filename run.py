#!/usr/bin/env python3
"""
Employee Attendance System - Startup Script
"""

import os
import sys
from app import app, create_sample_data

def main():
    """Main startup function"""
    print("=" * 50)
    print("Employee Attendance System")
    print("=" * 50)
    
    # Create sample data
    print("Initializing database...")
    create_sample_data()
    print("✓ Database initialized successfully!")

    # Public IP is no longer needed (IP-based restrictions removed)

    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))

    print(f"\nStarting server on http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    print("\n" + "=" * 50)

    # Show active geofence configuration at startup
    try:
        from config import Config
        print(
            f"Geofence config: office=({Config.OFFICE_LATITUDE}, {Config.OFFICE_LONGITUDE}) "
            f"radius={Config.OFFICE_RADIUS_METERS}m"
        )
    except Exception as e:
        print(f"⚠ Could not print geofence config: {e}")

    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True  # Force debug mode for development
    )

if __name__ == '__main__':
    main() 
