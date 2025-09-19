# EY Website Clone with Django

This is a clone of the EY website built with Django and Tailwind CSS, migrated from a Next.js project.

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

## Setup Instructions

### 1. Set up Python virtual environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Install Node.js dependencies

```bash
# Install Node.js dependencies
npm install

# Build Tailwind CSS
npm run build

# For development with auto-reload:
npm run dev
```

### 3. Set up the database

```bash
# Run migrations
python manage.py migrate

# Create a superuser (optional)
python manage.py createsuperuser
```

### 4. Run the development server

```bash
# In one terminal, run the Django server
python manage.py runserver

# In another terminal, run the Tailwind CSS watcher (if in development)
npm run dev
```

## Project Structure

- `core/` - Main Django app
  - `static/` - Static files (CSS, JS, images)
    - `css/` - Compiled CSS
    - `fonts/` - Custom fonts
    - `src/` - Source files (input.css)
  - `templates/` - Django templates
    - `partials/` - Reusable template components
- `ey_website/` - Django project settings

## Deployment

For production, make sure to:

1. Set `DEBUG = False` in settings.py
2. Run `npm run build` to generate production CSS
3. Collect static files: `python manage.py collectstatic`
4. Set up a production WSGI server (e.g., Gunicorn, uWSGI)
5. Set up a production database (e.g., PostgreSQL)

## License

This project is for educational purposes only.
