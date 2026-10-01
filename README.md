# MAFA Attendance System

A simple Flask + SQLite attendance system.

## Features
- Public student attendance form
- Stores student name, school, date and time
- Prevents the same name + school from being recorded twice on the same day
- Private admin login
- Search by student name
- Filter by school
- Filter by date
- Sort by name, school or date/time
- Export filtered results to CSV
- Mobile-friendly interface

## Run locally

```bash
python -m pip install -r requirements.txt
python app.py
```

Then open:
http://127.0.0.1:5000

Admin:
http://127.0.0.1:5000/admin/login

## Important before deployment

Set these environment variables on your hosting service:

- SECRET_KEY = a long random secret
- ADMIN_USERNAME = your admin username
- ADMIN_PASSWORD = a strong admin password

Do not publish real admin credentials in GitHub.

## Deployment

A Procfile is included:

web: gunicorn app:app
