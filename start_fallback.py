#!/usr/bin/env python3
"""
Fallback start script for Railway deployment - handles Firebase failures gracefully
"""

import os
import sys

print("🚀 Starting Flask app with Firebase fallback...")
print("Python version:", sys.version)
print("Current directory:", os.getcwd())

try:
    # Try to import the full app
    print("📦 Importing Flask app...")
    from app import app
    print("✅ App imported successfully")
    
    # Try Firebase setup, but don't fail if it doesn't work
    try:
        from railway_firebase import setup_firebase_for_railway
        setup_firebase_for_railway()
        print("✅ Firebase setup completed")
    except Exception as e:
        print(f"⚠️ Firebase setup failed: {e}")
        print("🔧 Continuing without Firebase...")
        # Set a flag to indicate Firebase is not available
        os.environ['FIREBASE_AVAILABLE'] = 'false'
    
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Starting server on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=False)
    
except Exception as e:
    print(f"❌ Error starting app: {str(e)}")
    import traceback
    traceback.print_exc()
    
    # Fallback to minimal app if full app fails
    print("🔄 Falling back to minimal app...")
    try:
        from flask import Flask, jsonify
        
        app = Flask(__name__)
        
        @app.route('/')
        def index():
            return jsonify({"message": "Flask app is running (fallback mode)!"})
        
        @app.route('/health')
        def health():
            return jsonify({"status": "healthy", "message": "Flask app is running (fallback)"}), 200
        
        port = int(os.environ.get('PORT', 5000))
        print(f"🌐 Starting fallback server on port {port}")
        
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e2:
        print(f"❌ Fallback also failed: {e2}")
        sys.exit(1)
