# 4-H GIS Website

A modern, animated portfolio website built with Flask, featuring a dark theme with purple accents and a complete authentication system. The website showcases The National 4-H Team's projects, about, and team and contact in a beautiful and interactive way.

## Features

- **Complete Authentication System**
  - User registration and login
  - Secure password hashing
  - Session management
  - User profiles
  - Remember me functionality

- **Database Integration**
  - SQLAlchemy ORM
  - User management
  - Contact form storage
  - PostgreSQL support for production

- **Modern Design**
  - Responsive design with dark theme
  - Animated elements using AOS (Animate On Scroll)
  - Interactive navigation
  - Project showcase
  - Contact form with database storage
  - Mobile-friendly layout

- **Production Ready**
  - Google Cloud App Engine deployment
  - Environment variable configuration
  - Security best practices
  - HTTPS enforcement

## Technologies Used

- **Backend**
  - Python 3.11
  - Flask 3.0.2
  - SQLAlchemy 3.1.1
  - Flask-Login 0.6.3
  - Flask-WTF 1.2.1
  - WTForms 3.1.1
  - PostgreSQL (production)

- **Frontend**
  - HTML5
  - CSS3
  - JavaScript
  - Font Awesome
  - AOS Library

- **Deployment**
  - Google Cloud App Engine
  - Gunicorn
  - Cloud SQL (PostgreSQL)

## Setup Instructions

### Local Development

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Globe_GIS_website
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Initialize the database:**
   ```bash
   python init_db.py
   ```

6. **Run the application:**
   ```bash
   python main.py
   ```

7. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on deploying to Google Cloud Platform.

## Authentication

The application includes a complete authentication system:

- **Registration:** Users can create accounts with username, email, and password
- **Login:** Secure login with remember me functionality
- **Profile:** Users can view their profile information
- **Logout:** Secure session termination

### Default Test User

After running `init_db.py`, a test user is created:
- Username: `admin`
- Password: `password123`
- Email: `admin@example.com`

**Important:** Change these credentials in production!

## Database Schema

### Users Table
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email address
- `password_hash` - Hashed password
- `first_name` - User's first name
- `last_name` - User's last name
- `created_at` - Account creation timestamp
- `last_login` - Last login timestamp
- `is_active` - Account status

### Contact Messages Table
- `id` - Primary key
- `name` - Sender's name
- `email` - Sender's email
- `subject` - Message subject
- `message` - Message content
- `timestamp` - Message timestamp
- `user_id` - Optional link to registered user

## Project Structure

```
Globe_GIS_website/
├── main.py              # Flask application
├── models.py            # Database models
├── forms.py             # WTForms definitions
├── init_db.py           # Database initialization
├── requirements.txt     # Python dependencies
├── app.yaml             # Google App Engine config
├── DEPLOYMENT.md        # Deployment guide
├── static/
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   └── images/         # Image assets
├── templates/          # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── about.html
│   ├── projects.html
│   ├── contact.html
│   ├── login.html
│   ├── register.html
│   └── profile.html
└── README.md
```

## Environment Variables

Set these environment variables for production:

- `SECRET_KEY` - Flask secret key for sessions
- `DATABASE_URL` - PostgreSQL connection string
- `FLASK_ENV` - Set to 'production' for production

## Security Features

- Password hashing using Werkzeug
- CSRF protection with Flask-WTF
- Secure session management
- HTTPS enforcement in production
- SQL injection protection via SQLAlchemy
- Input validation and sanitization



## License

This project is licensed under the MIT License - see the LICENSE file for details. 