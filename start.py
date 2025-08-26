#!/usr/bin/env python3
"""
Simple start script for Railway deployment
"""

import os
import sys

print("🚀 Starting Flask app on Railway...")
print("Python version:", sys.version)
print("Current directory:", os.getcwd())
print("Environment variables:")
print("- PORT:", os.environ.get('PORT', 'Not set'))
print("- DEBUG:", os.environ.get('DEBUG', 'Not set'))

try:
    print("📦 Importing Flask app...")
    from app import app
    print("✅ App imported successfully")
    
    # Test Firebase connection
    try:
        from railway_firebase import setup_firebase_for_railway
        setup_firebase_for_railway()
        print("✅ Firebase setup completed")
    except Exception as e:
        print(f"⚠️ Firebase setup warning: {e}")
        print("🔧 Continuing without Firebase...")
    
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Starting server on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=False)
    
except Exception as e:
    print(f"❌ Error starting app: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
