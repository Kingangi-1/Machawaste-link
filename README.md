# Create a basic README
@'
# Machawaste Link - Smart Waste Management Platform

A Django-based platform connecting waste posters with collectors and recyclers.

## Features

- Waste posting and categorization
- Digital credit system
- Waste matching between posters and collectors
- User dashboard with waste management

## Technology Stack

- Django 5.2
- Bootstrap 5
- SQLite (development)
- Python 3.13

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Create superuser: `python manage.py createsuperuser`
5. Run server: `python manage.py runserver`

## Project Structure

- `core/` - Main Django app with models, views, and templates
- `wastehub/` - Project settings and configuration
'@ | Out-File -FilePath "README.md" -Encoding UTF8

# Add and commit the README
git add README.md
git commit -m "Add README.md"
git push
