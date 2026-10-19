import os
import sqlite3
from datetime import datetime
from pathlib import Path

import click
from flask import g

BASE_DIR = Path(__file__).resolve().parent
SCHEMA = BASE_DIR / "schema.sql"
MIGRATIONS_DIR = BASE_DIR / "migrations"
SCHEMA_VERSION = 1

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


def _apply_migrations(conn):
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version < 1:
        migration = MIGRATIONS_DIR / "0001_add_indexes.sql"
        if migration.exists():
            with open(migration, encoding="utf-8") as f:
                conn.executescript(f.read())
        conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        conn.commit()


def init_db():
    conn = _direct_connection()
    try:
        with open(SCHEMA, encoding="utf-8") as f:
            conn.executescript(f.read())
        _apply_migrations(conn)
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


def backup_db(dest_dir=None):
    dest_dir = Path(dest_dir) if dest_dir else BASE_DIR / "backups"
    dest_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = dest_dir / f"foundation-{stamp}.sqlite3"
    src = sqlite3.connect(DATABASE)
    dst = sqlite3.connect(dest)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()
    return dest


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(seed_db_command)
    app.cli.add_command(backup_db_command)
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


@click.command("backup-db")
@click.option(
    "--dest-dir",
    default=None,
    help="Directory to write the backup into (default: backups/).",
)
def backup_db_command(dest_dir):
    """Write a consistent copy of the database into backups/."""
    path = backup_db(dest_dir)
    click.echo(f"Backup written to {path}")
