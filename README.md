# Employee Attendance System

A modern web-based employee attendance system with GPS geofence-based access control, built with Flask and SQLite.

## Features

### 🔐 Security Features
- **GPS Geofence Access Control**: Employee actions restricted to within office geofence
- **Admin Authentication**: Secure admin login with password hashing
- **Session Management**: Flask-Login for secure session handling

### 👥 Employee Features
- **Sign In/Out**: Simple employee ID-based attendance tracking
- **Working Hours Calculation**: Automatic calculation of total working hours
- **Real-time Feedback**: Immediate confirmation of sign-in/sign-out actions
- **Geofence Restriction**: Sign in/out only within office GPS geofence

### 👨‍💼 Admin Features
- **Dashboard**: Real-time attendance statistics and overview
- **Employee Management**: View all employees and their details
- **Attendance Records**: Comprehensive attendance history with filtering
- **Reports**: Date-based filtering and summary statistics
- **No IP Restrictions**: Admin can access from anywhere

### 🎨 User Interface
- **Modern Design**: Beautiful gradient-based UI with Bootstrap 5
- **Responsive**: Works on desktop, tablet, and mobile devices
- **Intuitive Navigation**: Easy-to-use interface for both employees and admins
- **Real-time Updates**: Live statistics and status indicators

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Clone or Download
```bash
# If using git
git clone <repository-url>
cd attendance-system

# Or download and extract the files
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

## Configuration

### Geofence Configuration
Configure the office location and radius via environment variables or in `config.py`:

```python
OFFICE_LATITUDE = 12.9208
OFFICE_LONGITUDE = 77.6180203
OFFICE_RADIUS_METERS = 400
```

### Admin Credentials
Default admin credentials:
- **Username**: `admin`
- **Password**: `admin123`

**Important**: Change these credentials in production!

## Usage

### For Employees
1. Connect to office WiFi
2. Visit the application URL
3. Click "Employee Access"
4. Enter your Employee ID
5. Choose Sign In or Sign Out

### For Admins
1. Visit the application URL
2. Click "Admin Access"
3. Login with admin credentials
4. Access dashboard, employee management, and attendance records

### Sample Employee IDs
The system comes with 5 sample employees for testing:
- `EMP001` - John Doe (IT)
- `EMP002` - Jane Smith (HR)
- `EMP003` - Mike Johnson (Sales)
- `EMP004` - Sarah Wilson (Marketing)
- `EMP005` - David Brown (Finance)

## Database

The system uses SQLite database (`attendance.db`) with the following tables:

### Employee Table
- Employee ID (unique)
- Name
- Email
- Department
- Active status

### Attendance Table
- Employee ID (foreign key)
- Date
- Sign-in time
- Sign-out time
- Total working hours
- Created timestamp

### Admin Table
- Username (unique)
- Password hash
- Name

## Security Considerations

### Production Deployment
1. **Change Default Credentials**: Update admin username/password
2. **Use Environment Variables**: Store sensitive data in environment variables
3. **HTTPS**: Enable SSL/TLS for secure communication
4. **Database Security**: Use a production database (PostgreSQL, MySQL)
5. Configure appropriate geofence and secure location permissions on client devices
6. **Regular Backups**: Implement database backup strategy

### Network Security
- Configure firewall rules
- Use VPN for remote admin access
- Monitor access logs
- Regular security updates

## API Endpoints

### Public Routes
- `/` - Main page
- `/employee` - Employee portal
- `/employee/signin` - Employee sign-in
- `/employee/signout` - Employee sign-out
- `/admin/login` - Admin login

### Protected Routes (Admin Only)
- `/admin/dashboard` - Admin dashboard
- `/admin/employees` - Employee management
- `/admin/attendance` - Attendance records
- `/admin/logout` - Admin logout

## Customization

### Adding New Features
1. **New Employee Fields**: Modify the Employee model in `app.py`
2. **Additional Reports**: Add new routes and templates
3. **Email Notifications**: Integrate email service
4. **Mobile App**: Create API endpoints for mobile integration

### Styling
- Modify CSS in `templates/base.html`
- Update Bootstrap classes
- Add custom JavaScript for enhanced functionality

## Troubleshooting

### Common Issues

1. **Access Denied Error**
   - Check if you're connected to office WiFi
   - Verify IP address configuration
   - Try accessing from localhost for testing

2. **Database Errors**
   - Delete `attendance.db` file and restart
   - Check file permissions
   - Verify SQLite installation

3. **Port Already in Use**
   - Change port in `app.py`: `app.run(port=5001)`
   - Kill existing process using the port

4. **Module Import Errors**
   - Verify all dependencies are installed
   - Check Python version compatibility
   - Reinstall requirements: `pip install -r requirements.txt`

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the code comments
3. Verify your configuration
4. Test with sample data first

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Note**: This is a demonstration system. For production use, implement additional security measures and follow best practices for web application security. 