# Life Connect Registry - Django Setup Instructions

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MySQL 8.0+ (or MariaDB)
- pip package manager

### Installation Steps

1. **Clone/Download the project**

   ```bash
   git clone <repository-url>
   cd LifeConnect_Registry
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env with your configuration
   # Set your database credentials, email settings, etc.
   ```

5. **Create database**

   ```sql
   CREATE DATABASE lifeconnect_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

6. **Run database migrations**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create superuser**

   ```bash
   python manage.py createsuperuser
   ```

8. **Collect static files**

   ```bash
   python manage.py collectstatic
   ```

9. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## 🌐 Access the Application

- **Main Website**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **User Dashboard**: http://localhost:8000/dashboard/
- **Admin Dashboard**: http://localhost:8000/admin-dashboard/

## 🔧 Configuration

### Database Setup

Update your `.env` file:

```env
DB_NAME=lifeconnect_db
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

### Email Configuration

For email notifications to work:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=info@lifeconnect.org
```

## 📋 Features Implemented

### ✅ Core Features

- **User Authentication**: Login with Registration ID or Email
- **Registration System**: Separate forms for Donors and Recipients
- **Unique ID Generation**: Auto-generated registration IDs (OD-DON-XXXXX, OD-REC-XXXXX)
- **Profile Management**: Complete user profiles with medical information
- **Document Upload**: File uploads for verification documents
- **Dashboard**: User and admin dashboards with statistics
- **Email Notifications**: Automated emails for registration status updates
- **Activity Logging**: Complete activity tracking system

### ✅ Admin Features

- **Django Admin**: Full admin interface for data management
- **Verification System**: Approve/reject user registrations
- **User Management**: View and manage all users
- **Statistics**: Real-time statistics dashboard
- **Email Communication**: Send emails to users from admin panel
- **Activity Monitoring**: Track all system activities

### ✅ Security Features

- **CSRF Protection**: Built-in Django CSRF protection
- **SQL Injection Prevention**: Django ORM protection
- **Password Validation**: Strong password requirements
- **Session Management**: Secure session handling
- **File Upload Security**: Secure file upload handling

## 🏗️ Project Structure

```
LifeConnect_Registry/
├── lifeconnect/           # Django project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── main/                # Main Django app
│   ├── __init__.py
│   ├── admin.py         # Django admin configuration
│   ├── apps.py
│   ├── forms.py         # Django forms
│   ├── models.py        # Database models
│   ├── urls.py          # App URL patterns
│   └── views.py         # View functions
├── static/              # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
├── templates/           # HTML templates
│   └── main/
├── media/               # User uploaded files
├── logs/                # Application logs
├── manage.py           # Django management script
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
└── README.md           # Project documentation
```

## 🗄️ Database Models

### User Model

- Custom user model extending Django's AbstractUser
- Fields: username, email, user_type, registration_id, phone, blood_group, etc.
- User types: donor, recipient, admin
- Auto-generated unique registration IDs

### DonorProfile Model

- Extended profile for organ donors
- Medical information, organs to donate, fitness status
- Document uploads for verification

### RecipientProfile Model

- Extended profile for organ recipients
- Medical requirements, hospital information
- Urgency levels and medical reports

### Supporting Models

- **Document**: File uploads and verification
- **VerificationRequest**: Track verification status
- **Message**: System notifications and communications
- **ActivityLog**: User activity tracking

## 📝️ API Endpoints

### Public Endpoints

- `GET /` - Home page
- `GET /about/` - About organ donation
- `GET /register/` - Registration page
- `POST /register/` - Submit registration
- `GET /login/` - Login page
- `POST /login/` - User authentication
- `GET /contact/` - Contact page
- `POST /contact/` - Submit contact form
- `GET /faq/` - FAQ page

### User Endpoints (Login Required)

- `GET /dashboard/` - User dashboard
- `POST /logout/` - User logout

### Admin Endpoints (Admin Required)

- `GET /admin-dashboard/` - Admin dashboard
- `POST /approve-user/<id>/` - Approve user
- `POST /reject-user/<id>/` - Reject user
- `POST /send-email/<id>/` - Send email to user

### AJAX Endpoints

- `POST /generate-id/` - Generate registration ID

## 🚀 Deployment

### Production Settings

1. Set `DEBUG=False` in `.env`
2. Configure `ALLOWED_HOSTS` with your domain
3. Set up production database
4. Configure email settings
5. Set up static file serving
6. Configure WSGI server (Gunicorn/Nginx)

### Gunicorn Command

```bash
gunicorn lifeconnect.wsgi:application --bind 0.0.0.0:8000
```

## 🔍 Testing

### Run Tests

```bash
python manage.py test
```

### Create Test Data

```bash
python manage.py shell
>>> from main.models import User
>>> User.objects.create_user(username='test', email='test@example.com', password='password123')
```

## 🐛 Common Issues & Solutions

### Database Connection Error

- Check MySQL service is running
- Verify database credentials in `.env`
- Ensure database exists and user has permissions

### Static Files Not Loading

- Run `python manage.py collectstatic`
- Check `STATIC_URL` and `STATIC_ROOT` settings
- Verify web server static file configuration

### Email Not Working

- Check email credentials in `.env`
- Verify SMTP server settings
- Check firewall/blocking issues

### Migration Errors

- Delete existing migrations: `rm -rf main/migrations/`
- Run `makemigrations` again
- Check model definitions for errors

## 📞 Support

For issues and questions:

- Check the logs in `logs/django.log`
- Review Django admin for data issues
- Test with development server first
- Check environment variables configuration

## 🔄 Updates & Maintenance

### Regular Tasks

- Update dependencies: `pip install -r requirements.txt --upgrade`
- Backup database regularly
- Monitor logs for errors
- Update security patches

### Adding New Features

1. Create models in `main/models.py`
2. Create forms in `main/forms.py`
3. Create views in `main/views.py`
4. Add URL patterns in `main/urls.py`
5. Create templates in `templates/main/`
6. Run migrations: `python manage.py makemigrations`
7. Apply migrations: `python manage.py migrate`

---

**Life Connect Registry** - Complete Django Organ Donation Platform 🏥

Built with ❤️ for saving lives through organ donation
