#!/usr/bin/env python3
"""
Railway-specific Firebase setup
"""

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

def setup_firebase_for_railway():
    """Setup Firebase for Railway deployment"""
    try:
        # Check if Firebase is already initialized
        firebase_admin.get_app()
        print("✅ Firebase already initialized")
        return firebase_admin.get_app()
    except ValueError:
        # Firebase not initialized, so initialize it
        pass
    
    try:
        # Option 1: Use FIREBASE_CREDENTIALS environment variable
        firebase_creds_json = os.environ.get('FIREBASE_CREDENTIALS')
        if firebase_creds_json:
            # Parse the JSON credentials from environment variable
            creds_dict = json.loads(firebase_creds_json)
            cred = credentials.Certificate(creds_dict)
            app = firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized with FIREBASE_CREDENTIALS")
            return app
        
        # Option 2: Use individual environment variables
        firebase_config = {
            "type": "service_account",
            "project_id": os.environ.get('FIREBASE_PROJECT_ID', 'duty-login'),
            "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID'),
            "private_key": os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
            "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL'),
            "client_id": os.environ.get('FIREBASE_CLIENT_ID'),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ.get('FIREBASE_CLIENT_CERT_URL')
        }
        
        if firebase_config['private_key']:
            cred = credentials.Certificate(firebase_config)
            app = firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized with individual environment variables")
            return app
        
        # Option 3: Use Application Default Credentials
        cred = credentials.ApplicationDefault()
        app = firebase_admin.initialize_app(cred, {
            'projectId': 'duty-login',
        })
        print("✅ Firebase initialized with Application Default Credentials")
        return app
        
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        print("🔧 Continuing without Firebase...")
        return None

def get_firestore_client():
    """Get Firestore client"""
    try:
        setup_firebase_for_railway()
        return firestore.client()
    except Exception as e:
        print(f"❌ Could not get Firestore client: {e}")
        return None
