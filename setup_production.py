#!/usr/bin/env python3
"""
Production Setup Script for Employee Attendance System
This script helps you set up secure environment variables for production deployment.
"""

import os
import secrets
import string
import sys

def generate_secret_key(length=32):
    """Generate a secure random secret key"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_secure_password(length=16):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_env_file():
    """Create a .env file with secure production settings"""
    
    print("🔒 Setting up Production Environment Variables")
    print("=" * 50)
    
    # Generate secure credentials
    secret_key = generate_secret_key(64)
    admin_password = generate_secure_password(20)
    
    env_content = f"""# Flask Configuration
SECRET_KEY={secret_key}
DEBUG=False

# Database Configuration
DATABASE_URL=sqlite:///instance/attendance.db

# Firebase Configuration
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/firebase-service-account.json

# Admin Configuration (Generated securely)
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD={admin_password}
DEFAULT_ADMIN_NAME=System Administrator

# Geofence Configuration
OFFICE_LATITUDE=12.92499
OFFICE_LONGITUDE=77.61800
OFFICE_RADIUS_METERS=1000

# Sample Data (Disabled for production)
SEED_SAMPLE_DATA=false
"""
    
    # Write to .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with secure settings")
    print(f"🔑 Generated Secret Key: {secret_key[:20]}...")
    print(f"👤 Generated Admin Password: {admin_password}")
    print("\n⚠️  IMPORTANT SECURITY NOTES:")
    print("1. Keep your .env file secure and never commit it to version control")
    print("2. Change the admin password after first login")
    print("3. Update Firebase credentials path")
    print("4. Set DEBUG=False in production")
    print("\n📝 Next steps:")
    print("1. Review and edit the .env file if needed")
    print("2. Set up your Firebase credentials")
    print("3. Deploy your application")

def main():
    """Main function"""
    if os.path.exists('.env'):
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    create_env_file()

if __name__ == '__main__':
    main()
