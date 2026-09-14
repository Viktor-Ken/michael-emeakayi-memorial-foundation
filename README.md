# Michael Emeakayi Memorial Foundation — Website

A lightweight, mobile-responsive MVP website for the Michael Emeakayi Memorial Foundation, built with Flask and SQLite. Pure web technology — no external services, no analytics, no payments.

## Pages

- **Home** — mission statement and calls to action
- **About** — story, vision and mission
- **Initiatives** — Education, Agriculture, IT Skills
- **Trustees** — board members from the database
- **Events** — events from the database
- **Contact** — working form that saves messages to the database
- **Admin** — add/edit/delete trustees, events and view contact messages (no authentication for MVP)

## Requirements

- Python 3.9+

## Run

```bash
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

The database (`foundation.db`) is created and seeded with sample trustees and events automatically on first start. Delete the file to reset to sample data.

To run on a custom port or host:

```bash
python app.py        # writes to foundation.db in the project folder
flask --app app run --port 8000
```

To use a different database location, set the `FOUNDATION_DB` environment variable:

```bash
set FOUNDATION_DB=C:\path\to\foundation.db
python app.py
```

## Tests

```bash
python tests.py
```

Runs the Flask test client against an isolated temporary database.

## Project structure

```
app.py               # Routes
db.py                # SQLite helpers (init, seed, query/scalar/execute)
schema.sql           # Table definitions
seed.sql             # Sample trustees and events
tests.py             # Integration tests
static/css/style.css # Styles (responsive, no frameworks)
templates/           # Jinja2 templates (public + admin/)
```

## Before going live

- Replace `SECRET_KEY` in `app.py`.
- Update the contact details on the Contact page.
- Deploy with a WSGI server (for example `waitress` or `gunicorn`) rather than Flask's built-in server.