# ZNAT - Cybersecurity Awareness Training Platform

ZNAT is a comprehensive cybersecurity awareness training platform built with Django, designed to help organizations train their employees in cybersecurity best practices through interactive courses and assessments.

## Features

- **User Role Management**
  - Admin and Employee roles with different access levels
  - Custom user authentication system
  - Role-based dashboard views

- **Course Management**
  - Multi-level course structure (Basic, Intermediate, Advanced)
  - Support for video and PDF learning materials
  - Course progress tracking
  - Course material upload with file size validation

- **Assessment System**
  - Interactive quizzes with multiple-choice questions
  - Automatic scoring and feedback
  - Configurable passing scores
  - Progress tracking and analytics

- **Admin Features**
  - Course creation and management
  - Quiz creation and management
  - User progress monitoring
  - Analytics dashboard with completion rates
  - Employee performance tracking

- **Employee Features**
  - Level-based course access
  - Interactive learning materials
  - Progress tracking
  - Assessment attempts tracking
  - Performance feedback

## Technology Stack

- **Backend**: Django 4.2
- **Database**: PostgreSQL 
- **Frontend**: 
  - HTML5, CSS3, JavaScript
  - Bootstrap 5
  - Font Awesome icons
  - Custom cybersecurity-themed UI

## Prerequisites

- Python 3.11 or higher
- PostgreSQL
- Virtual environment (recommended)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd znat
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the database in `znat/settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'znat_db',
           'USER': 'your_username',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

- `courses/`: Course management app
- `questions/`: Question and assessment management
- `quizzes/`: Quiz functionality and scoring
- `users/`: Custom user management
- `static/`: Static files (CSS, JavaScript)
- `templates/`: HTML templates
- `media/`: Uploaded files (videos, PDFs)

## File Upload Limits

- Video files: Maximum 100MB
- PDF files: Maximum 10MB

## Security Features

- Password strength validation
- Role-based access control
- File type validation
- Secure file upload handling
- CSRF protection
- Session security

## Development Guidelines

1. Follow Django's coding style
2. Write tests for new features
3. Document code changes
4. Validate file uploads
5. Implement proper error handling

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request