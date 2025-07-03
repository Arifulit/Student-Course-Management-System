# Course Management System

A comprehensive Django web application for managing student courses, enrollments, and file sharing.

## Student Information
- **Name:** [Your Name]
- **Student ID:** [Your Student ID]

## Features

### For Students:
- User registration and authentication
- Course browsing and enrollment (max 5 courses)
- File upload/download for course materials
- Personal dashboard with enrolled courses
- Profile management
- Course search functionality

### For Administrators:
- Admin panel for managing courses and students
- View all enrollments and uploaded files
- Comprehensive dashboard with statistics
- User management capabilities

## Technical Features

- **Django Framework:** Built with Django 4.2.7
- **Database:** SQLite (easily configurable for PostgreSQL/MySQL)
- **Authentication:** Django's built-in authentication system
- **File Management:** Secure file upload/download with permissions
- **Admin Interface:** Customized Django admin panel
- **Messages Framework:** User feedback for all actions
- **Responsive Design:** Bootstrap 5 for mobile-friendly interface
- **Search:** Course search functionality
- **Permissions:** Role-based access control

## Models

1. **Student** - Extended user profile with student-specific information
2. **Course** - Course information with enrollment limits
3. **Enrollment** - Many-to-many relationship between students and courses
4. **FileUpload** - File management with course association

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Create a virtual environment:**
   ```bash
   python -m venv course_management_env
   ```

2. **Activate the virtual environment:**
   
   On Windows:
   ```bash
   course_management_env\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source course_management_env/bin/activate
   ```

3. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (admin account):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

7. **Access the application:**
   - Main application: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Usage

### For Students:
1. Register for a new account at `/register/`
2. Log in to access the dashboard
3. Browse available courses at `/courses/`
4. Enroll in courses (maximum 5 courses)
5. Upload and download course materials
6. Manage your profile

### For Administrators:
1. Log in to the admin panel at `/admin/`
2. Add new courses and manage existing ones
3. View student enrollments and manage users
4. Monitor file uploads and system usage

## Project Structure

```
course_management/
├── course_management/          # Project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── students/                   # Main application
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── signals.py
│   ├── urls.py
│   └── views.py
├── templates/                  # HTML templates
│   ├── base.html
│   └── students/
├── media/                      # Uploaded files
├── manage.py
├── requirements.txt
└── README.md
```

## Security Features

- CSRF protection on all forms
- Login required decorators for protected views
- File upload restrictions (10MB max)
- Permission-based file access
- Role-based access control
- Secure file handling

## Validation Rules

- Students can enroll in maximum 5 courses
- Courses have maximum student limits
- File size restrictions (10MB)
- Unique student IDs
- Email validation
- Only file owners and admins can delete files

## Future Enhancements

- Email notifications for enrollments
- Grade management system
- Course calendar integration
- Advanced search and filtering
- Mobile app API
- Payment integration for paid courses

## Troubleshooting

### Common Issues:

1. **Database errors:** Run `python manage.py migrate` to apply pending migrations
2. **Static files not loading:** Ensure DEBUG=True in settings.py for development
3. **File upload errors:** Check media directory permissions
4. **Admin access:** Create superuser with `python manage.py createsuperuser`

### Development Tips:

- Use `python manage.py shell` to interact with the database
- Run `python manage.py collectstatic` before production deployment
- Check logs for detailed error information
- Use Django Debug Toolbar for development debugging

## License

This project is created for educational purposes as part of a Django learning assignment.