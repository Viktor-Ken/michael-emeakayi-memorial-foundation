import os
import sqlite3
from pathlib import Path

import click
from flask import current_app, g

BASE_DIR = Path(__file__).resolve().parent
SCHEMA = BASE_DIR / "schema.sql"

DATABASE = Path(
    os.environ.get("FOUNDATION_DB", str(BASE_DIR / "foundation.db"))
)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query(sql, args=()):
    return get_db().execute(sql, args).fetchall()


def scalar(sql, args=()):
    return get_db().execute(sql, args).fetchone()[0]


def execute(sql, args=(), commit=True):
    cur = get_db().execute(sql, args)
    if commit:
        get_db().commit()
    return cur.lastrowid


def _direct_connection():
    conn = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _direct_connection()
    try:
        with open(SCHEMA, encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
    finally:
        conn.close()


def seed_db():
    conn = _direct_connection()
    try:
        existing = conn.execute("SELECT COUNT(*) FROM trustees").fetchone()[0]
        if existing:
            return

        with open(BASE_DIR / "seed.sql", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
        click.echo("Seeded sample trustees and events.")
    finally:
        conn.close()


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(seed_db_command)
    with app.app_context():
        init_db()
        seed_db()


@click.command("init-db")
def init_db_command():
    """Create the database tables."""
    init_db()
    click.echo("Initialised the database.")


@click.command("seed-db")
def seed_db_command():
    """Load the sample (seed) data into the database."""
    seed_db()
    click.echo("Seeded the database.")