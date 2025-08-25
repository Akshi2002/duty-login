from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
import math

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Geofence-based access control is active

# Database Models
class Employee(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    def get_id(self):
        return f"employee-{self.id}"

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    def get_id(self):
        return f"admin-{self.id}"

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), db.ForeignKey('employee.employee_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    sign_in_time = db.Column(db.DateTime)
    sign_out_time = db.Column(db.DateTime)
    total_hours = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith("admin-"):
        return Admin.query.get(int(user_id.split("-")[1]))
    elif user_id.startswith("employee-"):
        return Employee.query.get(int(user_id.split("-")[1]))
    return None

# IP-based access has been removed in favor of GPS geofencing

def haversine_distance_m(lat1, lon1, lat2, lon2):
    R = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def is_within_office_geofence(lat, lon):
    if lat is None or lon is None:
        print(f"DEBUG Geofence: Missing coordinates lat={lat}, lon={lon}")
        return False
    try:
        user_lat = float(lat)
        user_lon = float(lon)
        
        # Use the new multi-location system
        is_within, office_name = Config.is_within_office_location(user_lat, user_lon)
        
        if is_within:
            print(f"DEBUG Geofence: user=({user_lat}, {user_lon}) is within {office_name}")
        else:
            print(f"DEBUG Geofence: user=({user_lat}, {user_lon}) is not within any office location")
            # Debug: show distances to all offices
            for office in Config.OFFICE_LOCATIONS:
                distance = haversine_distance_m(user_lat, user_lon, office['latitude'], office['longitude'])
                print(f"  - Distance to {office['name']}: {distance:.2f}m (radius: {office['radius_meters']}m)")
        
        return is_within
    except Exception as e:
        print(f"DEBUG Geofence error: {e} with lat={lat} lon={lon}")
        return False

@app.route('/')
def index():
    """Main page - redirects to appropriate login"""
    return render_template('index.html')

@app.route('/employee')
def employee_portal():
    """Employee portal"""
    return render_template('employee_portal.html', 
                         office_locations=Config.OFFICE_LOCATIONS,
                         office_lat=Config.OFFICE_LATITUDE, 
                         office_lng=Config.OFFICE_LONGITUDE, 
                         office_radius=Config.OFFICE_RADIUS_METERS)

@app.route('/employee/login', methods=['GET', 'POST'])
def employee_login():
    """Employee login functionality"""
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        password = request.form.get('password')
        lat = request.form.get('latitude')
        lon = request.form.get('longitude')
        print(f"DEBUG Route: /employee/login POST lat={lat} lon={lon}")
        
        # Enforce geofence for employee login
        if not is_within_office_geofence(lat, lon):
            flash('Access denied: You are not within any office location.', 'error')
            return render_template('employee_login.html', 
                                 office_locations=Config.OFFICE_LOCATIONS,
                                 office_lat=Config.OFFICE_LATITUDE, 
                                 office_lng=Config.OFFICE_LONGITUDE, 
                                 office_radius=Config.OFFICE_RADIUS_METERS)
        
        employee = Employee.query.filter_by(employee_id=employee_id, is_active=True).first()
        
        if not employee or not check_password_hash(employee.password_hash, password):
            flash('Invalid Employee ID or Password. Please check your credentials and try again.', 'error')
            return render_template('employee_login.html', 
                                 office_locations=Config.OFFICE_LOCATIONS,
                                 office_lat=Config.OFFICE_LATITUDE, 
                                 office_lng=Config.OFFICE_LONGITUDE, 
                                 office_radius=Config.OFFICE_RADIUS_METERS)

        # Login the employee
        login_user(employee)
        
        flash(f'Welcome {employee.name}! You have successfully logged in.', 'success')
        return redirect(url_for('employee_dashboard'))
    
    return render_template('employee_login.html', 
                         office_locations=Config.OFFICE_LOCATIONS,
                         office_lat=Config.OFFICE_LATITUDE, 
                         office_lng=Config.OFFICE_LONGITUDE, 
                         office_radius=Config.OFFICE_RADIUS_METERS)

@app.route('/employee/signin', methods=['GET', 'POST'])
@login_required
def employee_signin():
    """Employee sign-in functionality - requires login first"""
    if not isinstance(current_user, Employee):
        return redirect(url_for('employee_login'))
    
    if request.method == 'POST':
        # Employee is already logged in, just record attendance
        employee_id = current_user.employee_id
        lat = request.form.get('latitude')
        lon = request.form.get('longitude')
        print(f"DEBUG Route: /employee/signin POST lat={lat} lon={lon}")
        # Enforce geofence for sign-in
        if not is_within_office_geofence(lat, lon):
            flash('Sign-in denied: You are not within any office location.', 'error')
            return redirect(url_for('employee_dashboard'))
        
        today = datetime.now().date()
        existing_attendance = Attendance.query.filter_by(
            employee_id=employee_id, 
            date=today
        ).first()
        
        if existing_attendance and existing_attendance.sign_in_time:
            flash('You have already signed in today!', 'error')
            return redirect(url_for('employee_dashboard'))
        
        # Create new attendance record
        if not existing_attendance:
            attendance = Attendance(
                employee_id=employee_id,
                date=today,
                sign_in_time=datetime.now()
            )
            db.session.add(attendance)
        else:
            existing_attendance.sign_in_time = datetime.now()
        
        db.session.commit()
        
        flash(f'Welcome {current_user.name}! You have successfully signed in at {datetime.now().strftime("%H:%M:%S")}', 'success')
        return redirect(url_for('employee_dashboard'))
    
    return render_template('employee_signin.html', 
                         office_locations=Config.OFFICE_LOCATIONS,
                         office_lat=Config.OFFICE_LATITUDE, 
                         office_lng=Config.OFFICE_LONGITUDE, 
                         office_radius=Config.OFFICE_RADIUS_METERS)

@app.route('/employee/signout', methods=['GET', 'POST'])
@login_required
def employee_signout():
    """Employee sign-out functionality - requires login first"""
    if not isinstance(current_user, Employee):
        return redirect(url_for('employee_login'))
    
    # GET renders the sign-out page with geofence JS to capture location
    if request.method == 'GET':
        return render_template(
            'employee_signout.html',
            office_locations=Config.OFFICE_LOCATIONS,
            office_lat=Config.OFFICE_LATITUDE,
            office_lng=Config.OFFICE_LONGITUDE,
            office_radius=Config.OFFICE_RADIUS_METERS,
        )

    # POST: perform geofence check and complete sign-out
    lat = request.form.get('latitude')
    lon = request.form.get('longitude')
    print(f"DEBUG Route: /employee/signout POST lat={lat} lon={lon}")
    if not is_within_office_geofence(lat, lon):
        flash('Sign-out denied: You are not within any office location.', 'error')
        return redirect(url_for('employee_dashboard'))

    employee = current_user
    employee_id = employee.employee_id

    today = datetime.now().date()
    attendance = Attendance.query.filter_by(
        employee_id=employee_id,
        date=today
    ).first()

    if not attendance or not attendance.sign_in_time:
        flash('You have not signed in today!', 'error')
        return redirect(url_for('employee_dashboard'))

    if attendance.sign_out_time:
        flash('You have already signed out today!', 'error')
        return redirect(url_for('employee_dashboard'))

    # Calculate working hours
    sign_out_time = datetime.now()
    attendance.sign_out_time = sign_out_time

    time_diff = sign_out_time - attendance.sign_in_time
    total_hours = time_diff.total_seconds() / 3600
    attendance.total_hours = round(total_hours, 2)

    db.session.commit()

    hours = int(total_hours)
    minutes = int((total_hours - hours) * 60)

    flash(
        f'Goodbye {employee.name}! You have worked for {hours} hours and {minutes} minutes today.',
        'success'
    )
    return redirect(url_for('employee_dashboard'))

@app.route('/employee/dashboard')
@login_required
def employee_dashboard():
    """Employee dashboard - shows personal attendance info"""
    if not isinstance(current_user, Employee):
        return redirect(url_for('employee_portal'))
    
    # Get today's attendance for this employee
    today = datetime.now().date()
    today_attendance = Attendance.query.filter_by(
        employee_id=current_user.employee_id, 
        date=today
    ).first()
    
    # Get recent attendance records (last 10 days)
    recent_attendance = Attendance.query.filter_by(
        employee_id=current_user.employee_id
    ).order_by(Attendance.date.desc()).limit(10).all()
    
    return render_template('employee_dashboard.html',
                         today_attendance=today_attendance,
                         recent_attendance=recent_attendance)

@app.route('/employee/attendance')
@login_required
def employee_attendance():
    """Employee attendance records - read-only view"""
    if not isinstance(current_user, Employee):
        return redirect(url_for('employee_portal'))
    
    # Get date filter
    date_filter = request.args.get('date')
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            attendance_records = Attendance.query.filter_by(
                employee_id=current_user.employee_id, 
                date=filter_date
            ).order_by(Attendance.date.desc()).all()
        except ValueError:
            attendance_records = Attendance.query.filter_by(
                employee_id=current_user.employee_id
            ).order_by(Attendance.date.desc()).limit(50).all()
    else:
        attendance_records = Attendance.query.filter_by(
            employee_id=current_user.employee_id
        ).order_by(Attendance.date.desc()).limit(50).all()
    
    # Calculate statistics
    total_days = len(attendance_records)
    total_hours = sum([r.total_hours or 0 for r in attendance_records])
    complete_days = len([r for r in attendance_records if r.sign_in_time and r.sign_out_time])
    
    # Calculate average hours per day
    avg_hours_per_day = total_hours / total_days if total_days > 0 else 0
    
    # Calculate average sign-in and sign-out times
    signin_times = [r.sign_in_time for r in attendance_records if r.sign_in_time]
    signout_times = [r.sign_out_time for r in attendance_records if r.sign_out_time]
    
    avg_signin_time = "09:00"  # Default
    avg_signout_time = "17:00"  # Default
    
    if signin_times:
        avg_hour = sum([t.hour for t in signin_times]) / len(signin_times)
        avg_minute = sum([t.minute for t in signin_times]) / len(signin_times)
        avg_signin_time = f"{int(avg_hour):02d}:{int(avg_minute):02d}"
    
    if signout_times:
        avg_hour = sum([t.hour for t in signout_times]) / len(signout_times)
        avg_minute = sum([t.minute for t in signout_times]) / len(signout_times)
        avg_signout_time = f"{int(avg_hour):02d}:{int(avg_minute):02d}"
    
    stats = {
        'total_days': total_days,
        'total_hours': total_hours,
        'complete_days': complete_days,
        'avg_hours_per_day': avg_hours_per_day,
        'avg_signin_time': avg_signin_time,
        'avg_signout_time': avg_signout_time
    }
    
    return render_template('employee_attendance_view.html',
                         attendance_records=attendance_records,
                         stats=stats)

@app.route('/employee/logout')
@login_required
def employee_logout():
    """Employee logout"""
    if not isinstance(current_user, Employee):
        return redirect(url_for('employee_portal'))
    
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/employee/change_password', methods=['GET', 'POST'])
@login_required
def employee_change_password():
	"""Allow an employee to change their own password"""
	if not isinstance(current_user, Employee):
		return redirect(url_for('employee_portal'))

	if request.method == 'POST':
		current_password = request.form.get('current_password', '')
		new_password = request.form.get('new_password', '')
		confirm_password = request.form.get('confirm_password', '')

		# Validate inputs
		if not current_password or not new_password or not confirm_password:
			flash('Please fill in all password fields.', 'error')
			return render_template('employee_change_password.html')

		if not check_password_hash(current_user.password_hash, current_password):
			flash('Current password is incorrect.', 'error')
			return render_template('employee_change_password.html')

		if new_password != confirm_password:
			flash('New password and confirmation do not match.', 'error')
			return render_template('employee_change_password.html')

		if len(new_password) < 6:
			flash('New password must be at least 6 characters long.', 'error')
			return render_template('employee_change_password.html')

		# Update password
		current_user.password_hash = generate_password_hash(new_password)
		try:
			db.session.commit()
			flash('Your password has been changed successfully.', 'success')
			return redirect(url_for('employee_dashboard'))
		except Exception:
			db.session.rollback()
			flash('Error updating password. Please try again.', 'error')
			return render_template('employee_change_password.html')

	return render_template('employee_change_password.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    if not isinstance(current_user, Admin):
        return redirect(url_for('admin_login'))
    
    # Get today's attendance
    today = datetime.now().date()
    today_attendance = Attendance.query.filter_by(date=today).all()
    
    # Get all employees
    employees = Employee.query.filter_by(is_active=True).all()
    
    # Get attendance statistics
    total_employees = len(employees)
    signed_in_today = len([a for a in today_attendance if a.sign_in_time and not a.sign_out_time])
    signed_out_today = len([a for a in today_attendance if a.sign_out_time])
    
    return render_template('admin_dashboard.html',
                         employees=employees,
                         today_attendance=today_attendance,
                         total_employees=total_employees,
                         signed_in_today=signed_in_today,
                         signed_out_today=signed_out_today,
                         datetime=datetime)

@app.route('/admin/employees')
@login_required
def admin_employees():
    """Admin employee management"""
    if not isinstance(current_user, Admin):
        return redirect(url_for('admin_login'))
    
    employees = Employee.query.all()
    return render_template('admin_employees.html', employees=employees)

@app.route('/admin/employees/add', methods=['GET', 'POST'])
@login_required
def admin_add_employee():
    """Add new employee"""
    if not isinstance(current_user, Admin):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        name = request.form.get('name')
        email = request.form.get('email')
        department = request.form.get('department')
        password = request.form.get('password')

        # Validate required fields
        if not all([employee_id, name, email, department, password]):
            flash('All fields are required, including password!', 'error')
            return render_template('admin_add_employee.html')

        # Check if employee ID already exists
        existing_employee = Employee.query.filter_by(employee_id=employee_id).first()
        if existing_employee:
            flash('Employee ID already exists!', 'error')
            return render_template('admin_add_employee.html')

        # Check if email already exists
        existing_email = Employee.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already exists!', 'error')
            return render_template('admin_add_employee.html')

        # Hash the password
        password_hash = generate_password_hash(password)

        # Create new employee
        new_employee = Employee(
            employee_id=employee_id,
            name=name,
            email=email,
            department=department,
            password_hash=password_hash,
            is_active=True
        )

        try:
            db.session.add(new_employee)
            db.session.commit()
            flash(f'Employee {name} (ID: {employee_id}) has been added successfully!', 'success')
            return redirect(url_for('admin_employees'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding employee. Please try again.', 'error')
            return render_template('admin_add_employee.html')

    return render_template('admin_add_employee.html')

@app.route('/admin/employees/<int:employee_id>/toggle_status', methods=['POST'])
@login_required
def admin_toggle_employee_status(employee_id):
    """Toggle employee active/inactive status"""
    if not isinstance(current_user, Admin):
        return redirect(url_for('admin_login'))
    
    employee = Employee.query.get_or_404(employee_id)
    employee.is_active = not employee.is_active
    
    try:
        db.session.commit()
        status = "activated" if employee.is_active else "deactivated"
        flash(f'Employee {employee.name} has been {status} successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating employee status. Please try again.', 'error')
    
    return redirect(url_for('admin_employees'))

@app.route('/admin/employees/<int:employee_id>/delete', methods=['POST'])
@login_required
def admin_delete_employee(employee_id):
    """Permanently delete an employee and their attendance records"""
    if not isinstance(current_user, Admin):
        return redirect(url_for('admin_login'))

    employee = Employee.query.get_or_404(employee_id)
    try:
        print(f"DEBUG: Deleting employee id={employee.id}, employee_id={employee.employee_id}")
        # Remove all attendance records for this employee first
        Attendance.query.filter(Attendance.employee_id == employee.employee_id).delete(synchronize_session=False)
        db.session.delete(employee)
        db.session.commit()
        flash(f'Employee {employee.name} and their attendance records have been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"ERROR deleting employee id={employee.id}: {e}")
        flash('Error deleting employee. Please try again.', 'error')

    return redirect(url_for('admin_employees'))

@app.route('/admin/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_employee(employee_id):
    """Edit existing employee"""
    if not isinstance(current_user, Admin):
        return redirect(url_for('admin_login'))
    
    employee = Employee.query.get_or_404(employee_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        department = request.form.get('department')
        password = request.form.get('password')
        
        # Validate required fields
        if not all([name, email, department]):
            flash('All fields are required!', 'error')
            return render_template('admin_edit_employee.html', employee=employee)
        
        # Check if email already exists (excluding current employee)
        existing_email = Employee.query.filter_by(email=email).first()
        if existing_email and existing_email.id != employee.id:
            flash('Email already exists!', 'error')
            return render_template('admin_edit_employee.html', employee=employee)
        
        # Update employee
        employee.name = name
        employee.email = email
        employee.department = department
        
        # Update password if provided
        if password:
            employee.password_hash = generate_password_hash(password)
        
        try:
            db.session.commit()
            if password:
                flash(f'Employee {employee.name} has been updated successfully (password changed).', 'success')
            else:
                flash(f'Employee {employee.name} has been updated successfully!', 'success')
            return redirect(url_for('admin_employees'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating employee. Please try again.', 'error')
            return render_template('admin_edit_employee.html', employee=employee)
    
    return render_template('admin_edit_employee.html', employee=employee)

@app.route('/admin/attendance')
@login_required
def admin_attendance():
    """Admin attendance records"""
    if not isinstance(current_user, Admin):
        return redirect(url_for('admin_login'))
    
    # Get date filter
    date_filter = request.args.get('date')
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            attendance_records = Attendance.query.filter_by(date=filter_date).all()
        except ValueError:
            attendance_records = Attendance.query.order_by(Attendance.date.desc()).limit(100).all()
    else:
        attendance_records = Attendance.query.order_by(Attendance.date.desc()).limit(100).all()
    
    employees = Employee.query.all()
    return render_template('admin_attendance.html', attendance_records=attendance_records, employees=employees)

@app.route('/admin/logout')
@login_required
def admin_logout():
    """Admin logout"""
    logout_user()
    return redirect(url_for('index'))

def create_sample_data():
    """Create sample data for testing"""
    with app.app_context():
        db.create_all()
        # Always ensure there is at least one admin; seed default if none
        if Admin.query.count() == 0 and not Admin.query.filter_by(username=Config.DEFAULT_ADMIN_USERNAME).first():
            admin = Admin(
                username=Config.DEFAULT_ADMIN_USERNAME,
                password_hash=generate_password_hash(Config.DEFAULT_ADMIN_PASSWORD),
                name=Config.DEFAULT_ADMIN_NAME
            )
            db.session.add(admin)
            db.session.commit()
        
        if Config.SEED_SAMPLE_DATA:
            
            # Create sample employees
            if Employee.query.count() == 0:
                for emp_data in Config.SAMPLE_EMPLOYEES:
                    if not Employee.query.filter_by(employee_id=emp_data['employee_id']).first():
                        emp_copy = dict(emp_data)
                        # Hash the password before creating employee
                        password = emp_copy.pop('password')
                        emp_copy['password_hash'] = generate_password_hash(password)
                        employee = Employee(**emp_copy)
                        db.session.add(employee)
            
            db.session.commit()

if __name__ == '__main__':
    create_sample_data()
    app.run(debug=True, host='0.0.0.0', port=5000) 
