# License Management System

This project is a Django-based application designed to manage and automate the lifecycle of software licenses. It serves as a showcase of my expertise in Python and Django, highlighting key skills such as:

- Database modeling
- REST API development
- Integration with external services
- Use of Django's built-in features like middleware, signals, and management commands

## Features

- **License Management**: Manage software licenses efficiently with CRUD functionality.
- **API Integration**: Includes integrations like payment systems (`cryptomus.py`).
- **Custom Middleware and Signals**: Demonstrates advanced Django features for event-driven actions.
- **Scheduler**: Automates periodic tasks using custom scripts (`scheduler.py`).
- **Localization**: Supports multi-language functionality with Django's localization tools.
- **File Handling**: Includes media uploads and file management.
- **Notification Services**: Sends backups or notifications via Telegram (`send_backup_to_telegram.py`).
- **Templating**: Custom filters and template tags for dynamic content rendering.

## Technologies Used

- **Framework**: Django 4.x
- **Database**: SQLite (can be replaced with other databases)
- **Languages**: Python, HTML, CSS
- **Others**: Telegram Bot API, Payment Gateway Integration, Cron Jobs

## Project Structure

```
LicenseManagement/
├── LicenseManagement/       # Core project settings and configurations
├── licenses/                # Main application for license management
│   ├── migrations/          # Database migrations
│   ├── templates/           # HTML templates for the frontend
│   ├── static/              # Static files (CSS, JS, images)
│   ├── models.py            # Database models
│   ├── views.py             # Django views
│   ├── urls.py              # URL routing for the app
│   ├── api_views.py         # RESTful API endpoints
│   ├── forms.py             # Django forms
│   ├── scheduler.py         # Task scheduler
│   └── utils.py             # Utility functions
├── manage.py                # Django management script
├── db.sqlite3               # SQLite database (for development)
├── send_backup_to_telegram.py # Custom script for backup notifications
└── media/                   # Uploaded media files
```

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/aliansari22/Django-License-Management.git
   cd Django-License-Management
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:

   ```bash
   cd LicenseManagement
   python manage.py migrate
   ```

5. Run the development server:

   ```bash
   python manage.py runserver
   ```

6. Access the application at `http://127.0.0.1:8000/`.

## License

This project is licensed under the MIT License.
