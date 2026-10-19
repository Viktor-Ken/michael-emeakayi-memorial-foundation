# Michael Emeakayi Memorial Foundation — Website

A lightweight, mobile-responsive MVP website for the Michael Emeakayi Memorial Foundation, built with Flask and SQLite. Pure web technology — no external services, no analytics, no payments.

## Pages

- **Home** — mission statement and calls to action
- **About** — story, vision and mission
- **Initiatives** — Education, Agriculture, IT Skills
- **Trustees** — board members from the database
- **Events** — events from the database
- **Contact** — working form that saves messages to the database
- **Admin** — add/edit/delete trustees and events, view contact messages (no login for the MVP; authentication can be added later)

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

## Production server

```bash
pip install waitress
python wsgi.py        # serves on http://0.0.0.0:8000
```

## Backup the database

```bash
flask --app app backup-db
```

Writes a consistent copy into `backups/` (gitignored).

## Tests

```bash
python tests.py
```

Runs the Flask test client against an isolated temporary database (includes CSRF, security header, validation and 404 checks).

## Quality checks

```bash
pip install -r requirements-dev.txt
ruff check .
mypy
bandit -q -r app.py db.py validators.py wsgi.py
pip-audit -r requirements.txt
coverage run -m unittest && coverage report
```

A live smoke test against a running server:

```bash
BASE_URL=http://127.0.0.1:5000 python scripts/smoke.py
```

## Project structure

```
app.py               # Routes, security headers, error handlers
db.py                # SQLite helpers (init, seed, migrate, backup, query/scalar/execute)
validators.py        # Input length/format validation
schema.sql           # Table definitions
seed.sql             # Sample trustees and events
migrations/          # Versioned SQL migrations (PRAGMA user_version)
wsgi.py              # Waitress production entry point
scripts/smoke.py     # Live smoke checks
tests.py             # Integration tests
static/css/style.css # Styles (responsive, no frameworks)
static/js/main.js    # Nav toggle and delete-confirm handler
templates/           # Jinja2 templates (public + admin/ + errors/)
```

## Before going live

- Set a strong `SECRET_KEY` environment variable (session signing).
- Set `SECURE_COOKIES=1` once the site is behind HTTPS.
- Update the contact details on the Contact page.
- For a step-by-step free launch, see [DEPLOYMENT.md](DEPLOYMENT.md) (PythonAnywhere).
- The admin area has no password yet — keep `/admin` private (do not link it publicly) until authentication is added.
