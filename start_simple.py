#!/usr/bin/env python3
"""
Simple start script for Railway deployment - minimal version
"""

import os
import sys

print("🚀 Starting minimal Flask app on Railway...")
print("Python version:", sys.version)
print("Current directory:", os.getcwd())

try:
    # Create a minimal Flask app for testing
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return jsonify({"message": "Flask app is running!"})
    
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy", "message": "Flask app is running"}), 200
    
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Starting minimal server on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=False)
    
except Exception as e:
    print(f"❌ Error starting minimal app: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
