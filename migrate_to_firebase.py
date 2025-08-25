#!/usr/bin/env python3
"""
Migration script to move data from SQLite to Firebase Firestore
"""

import os
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def migrate_sqlite_to_firebase():
    """Migrate data from SQLite to Firebase"""
    
    print("🔄 Starting SQLite to Firebase migration...")
    
    try:
        # Import SQLite models
        from app import db, Employee, Admin, Attendance
        from firebase_models import FirebaseEmployee, FirebaseAdmin, FirebaseAttendance
        from firebase_service import get_firebase_service
        
        # Initialize Firebase
        firebase_service = get_firebase_service()
        print("✅ Firebase connection established")
        
        # Migrate Admins
        print("\n👨‍💼 Migrating Admins...")
        sqlite_admins = Admin.query.all()
        migrated_admins = 0
        
        for admin in sqlite_admins:
            # Check if admin already exists in Firebase
            existing_admin = FirebaseAdmin.find_by_username(admin.username)
            if existing_admin:
                print(f"⏭️  Admin {admin.username} already exists in Firebase")
                continue
                
            firebase_admin = FirebaseAdmin({
                'username': admin.username,
                'password_hash': admin.password_hash,
                'name': admin.name
            })
            
            if firebase_admin.save():
                print(f"✅ Migrated admin: {admin.username}")
                migrated_admins += 1
            else:
                print(f"❌ Failed to migrate admin: {admin.username}")
        
        print(f"✅ Migrated {migrated_admins} admins")
        
        # Migrate Employees
        print("\n👥 Migrating Employees...")
        sqlite_employees = Employee.query.all()
        migrated_employees = 0
        
        for employee in sqlite_employees:
            # Check if employee already exists in Firebase
            existing_employee = FirebaseEmployee.find_by_employee_id(employee.employee_id)
            if existing_employee:
                print(f"⏭️  Employee {employee.employee_id} already exists in Firebase")
                continue
                
            firebase_employee = FirebaseEmployee({
                'employee_id': employee.employee_id,
                'name': employee.name,
                'email': employee.email,
                'department': employee.department,
                'password_hash': employee.password_hash,
                'is_active': employee.is_active
            })
            
            if firebase_employee.save():
                print(f"✅ Migrated employee: {employee.employee_id} ({employee.name})")
                migrated_employees += 1
            else:
                print(f"❌ Failed to migrate employee: {employee.employee_id}")
        
        print(f"✅ Migrated {migrated_employees} employees")
        
        # Migrate Attendance Records
        print("\n📋 Migrating Attendance Records...")
        sqlite_attendance = Attendance.query.all()
        migrated_attendance = 0
        
        for attendance in sqlite_attendance:
            # Check if attendance record already exists in Firebase
            date_str = attendance.date.strftime('%Y-%m-%d')
            existing_attendance = FirebaseAttendance.find_by_employee_and_date(
                attendance.employee_id, 
                attendance.date
            )
            if existing_attendance:
                print(f"⏭️  Attendance for {attendance.employee_id} on {date_str} already exists")
                continue
            
            # Convert datetime objects to ISO strings
            sign_in_time_str = None
            sign_out_time_str = None
            
            if attendance.sign_in_time:
                sign_in_time_str = attendance.sign_in_time.isoformat()
            if attendance.sign_out_time:
                sign_out_time_str = attendance.sign_out_time.isoformat()
                
            firebase_attendance = FirebaseAttendance({
                'employee_id': attendance.employee_id,
                'date': date_str,
                'sign_in_time': sign_in_time_str,
                'sign_out_time': sign_out_time_str,
                'total_hours': attendance.total_hours
            })
            
            if firebase_attendance.save():
                print(f"✅ Migrated attendance: {attendance.employee_id} - {date_str}")
                migrated_attendance += 1
            else:
                print(f"❌ Failed to migrate attendance: {attendance.employee_id} - {date_str}")
        
        print(f"✅ Migrated {migrated_attendance} attendance records")
        
        print("\n🎉 Migration completed successfully!")
        print(f"📊 Summary:")
        print(f"   • Admins: {migrated_admins}")
        print(f"   • Employees: {migrated_employees}")
        print(f"   • Attendance Records: {migrated_attendance}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have both SQLite app and Firebase dependencies installed")
        return False
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True

def verify_migration():
    """Verify that migration was successful"""
    print("\n🔍 Verifying migration...")
    
    try:
        from firebase_models import FirebaseEmployee, FirebaseAdmin, FirebaseAttendance
        
        # Count Firebase records
        admins = FirebaseAdmin.find_by_username('admin')  # Check if default admin exists
        employees = FirebaseEmployee.get_all()
        attendance = FirebaseAttendance.get_recent(limit=1000)
        
        print(f"📊 Firebase Database Contents:")
        print(f"   • Default Admin: {'✅ Found' if admins else '❌ Not found'}")
        print(f"   • Employees: {len(employees)}")
        print(f"   • Attendance Records: {len(attendance)}")
        
        if employees:
            print(f"\n👥 Sample Employees:")
            for emp in employees[:3]:  # Show first 3
                print(f"   • {emp.employee_id}: {emp.name} ({emp.department})")
            if len(employees) > 3:
                print(f"   • ... and {len(employees) - 3} more")
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == '__main__':
    print("🔥 Firebase Migration Tool")
    print("=" * 50)
    
    # Check if Firebase is set up
    try:
        from firebase_service import get_firebase_service
        firebase_service = get_firebase_service()
        print("✅ Firebase connection test passed")
    except Exception as e:
        print(f"❌ Firebase connection failed: {e}")
        print("\n📋 Please complete Firebase setup first:")
        print("1. Install dependencies: pip install firebase-admin google-cloud-firestore")
        print("2. Set up Firebase service account (see firebase_setup_guide.md)")
        print("3. Run this migration script again")
        sys.exit(1)
    
    # Perform migration
    if migrate_sqlite_to_firebase():
        verify_migration()
        print("\n✅ Migration completed! You can now use app_firebase.py")
        print("💡 To switch to Firebase: rename app.py to app_sqlite.py and rename app_firebase.py to app.py")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)

