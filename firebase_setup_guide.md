# Firebase Setup Guide

## 🔥 Setting up Firebase for your Attendance System

### 1. Firebase Project Setup ✅ (Already Done)
You've already created your Firebase project: **duty-login**

### 2. Enable Firestore Database
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your **duty-login** project
3. Click **Firestore Database** in the left sidebar
4. Click **Create database**
5. Choose **Start in test mode** (for development)
6. Select a location close to you

### 3. Generate Service Account Key
1. In Firebase Console, go to **Project Settings** (gear icon)
2. Click the **Service accounts** tab
3. Click **Generate new private key**
4. Save the downloaded JSON file as `firebase-service-account.json` in your project root
5. **IMPORTANT**: Add this file to `.gitignore` to keep credentials secure

### 4. Install Dependencies
```bash
pip install firebase-admin google-cloud-firestore
```

### 5. Configuration Options

#### Option A: Service Account File (Recommended)
- Place `firebase-service-account.json` in your project root
- The system will automatically detect and use it

#### Option B: Environment Variables
Set these environment variables in your system or `.env` file:
```bash
FIREBASE_PRIVATE_KEY_ID=your_private_key_id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour_private_key_here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your_service_account_email@duty-login.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your_client_id
FIREBASE_CLIENT_CERT_URL=your_client_cert_url
```

#### Option C: Google Cloud Application Default Credentials
If running on Google Cloud, the system will use default credentials automatically.

### 6. Database Structure
Your Firestore database will have these collections:

#### `employees` collection:
```json
{
  "employee_id": "EMP001",
  "name": "John Doe",
  "email": "john@company.com",
  "department": "IT",
  "password_hash": "hashed_password",
  "is_active": true,
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

#### `admins` collection:
```json
{
  "username": "admin",
  "password_hash": "hashed_password", 
  "name": "System Administrator",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

#### `attendance` collection:
```json
{
  "employee_id": "EMP001",
  "date": "2024-01-15",
  "sign_in_time": "2024-01-15T09:00:00",
  "sign_out_time": "2024-01-15T17:00:00",
  "total_hours": 8.0,
  "created_at": "timestamp"
}
```

### 7. Security Rules (Production)
For production, update Firestore rules:
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow read/write access on all documents to any user signed in to the application
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

### 8. Migration from SQLite
Your existing SQLite data can be migrated to Firebase using the migration script that will be created.

### 9. Backup and Recovery
- Firebase automatically backs up your data
- You can export/import data using the Firebase CLI
- Set up automated backups for production

### 🚀 You're Ready!
Once you complete the Firebase setup, your attendance system will use Firestore for all data storage with real-time capabilities and automatic scaling!

