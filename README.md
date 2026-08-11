# Event Registration & Management System

This Django project provides a database-driven event registration and management experience with:

- separate admin and user authentication flows
- admin dashboard with real database counts
- event categories, events, registrations, wishlists, notifications, and settings
- user dashboard for browsing and joining events
- theme preferences and reusable templates

## Run locally

1. Create and activate a virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Start the dev server: `python manage.py runserver`

## Notes

- The app uses SQLite by default.
- New accounts are created through the signup flow.
- Admin access requires a staff account created via Django admin or shell.
