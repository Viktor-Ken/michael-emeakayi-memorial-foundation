import os

from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError

import db
import validators as v

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "change-this-secret-key-before-deploying"
)
app.config["MAX_CONTENT_LENGTH"] = 1_000_000
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SECURE_COOKIES", "") == "1"

csrf = CSRFProtect(app)
db.init_app(app)


@app.after_request
def set_security_headers(response):
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "img-src 'self' data:; base-uri 'self'; form-action 'self'; frame-ancestors 'none'",
    )
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault(
        "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
    )
    return response


@app.errorhandler(CSRFError)
def handle_csrf_error(error):
    return (
        render_template(
            "errors/error.html",
            code=400,
            message="The form expired. Please go back and try again.",
        ),
        400,
    )


@app.errorhandler(404)
def not_found(error):
    return (
        render_template(
            "errors/error.html",
            code=404,
            message="The page you are looking for does not exist.",
        ),
        404,
    )


@app.errorhandler(500)
def server_error(error):
    return (
        render_template(
            "errors/error.html",
            code=500,
            message="Something went wrong on our end. Please try again later.",
        ),
        500,
    )


@app.route("/")
def index():
    events = db.query("SELECT * FROM events ORDER BY date DESC LIMIT 3")
    return render_template("index.html", events=events)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/initiatives")
def initiatives():
    return render_template("initiatives.html")


@app.route("/trustees")
def trustees():
    rows = db.query("SELECT * FROM trustees ORDER BY id ASC")
    return render_template("trustees.html", trustees=rows)


@app.route("/events")
def events():
    rows = db.query("SELECT * FROM events ORDER BY date DESC")
    return render_template("events.html", events=rows)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        error = v.validate_contact(name, email, subject, message)
        if error:
            flash(error, "error")
        else:
            db.execute(
                "INSERT INTO messages (name, email, subject, message) VALUES (?, ?, ?, ?)",
                (name, email, subject, message),
            )
            flash("Thank you! Your message has been sent. We will be in touch soon.", "success")
            return redirect(url_for("contact"))

    return render_template("contact.html")


@app.route("/admin")
def admin_dashboard():
    counts = {
        "trustees": db.scalar("SELECT COUNT(*) FROM trustees"),
        "events": db.scalar("SELECT COUNT(*) FROM events"),
        "messages": db.scalar("SELECT COUNT(*) FROM messages"),
    }
    recent = db.query(
        "SELECT id, name, subject, created_at FROM messages ORDER BY created_at DESC LIMIT 5"
    )
    return render_template("admin/dashboard.html", counts=counts, recent=recent)


@app.route("/admin/trustees")
def admin_trustees():
    rows = db.query("SELECT * FROM trustees ORDER BY id ASC")
    return render_template("admin/trustees.html", trustees=rows)


def _trustee_form(mode, tid=None):
    trustee = None
    if mode == "edit":
        row = db.query("SELECT * FROM trustees WHERE id = ?", (tid,))
        if not row:
            abort(404)
        trustee = row[0]

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        role = request.form.get("role", "").strip()
        bio = request.form.get("bio", "").strip()
        error = v.validate_trustee(name, role, bio)
        if error:
            flash(error, "error")
        else:
            if mode == "edit":
                db.execute(
                    "UPDATE trustees SET name = ?, role = ?, bio = ? WHERE id = ?",
                    (name, role, bio, tid),
                )
                flash("Trustee updated.", "success")
            else:
                db.execute(
                    "INSERT INTO trustees (name, role, bio) VALUES (?, ?, ?)",
                    (name, role, bio),
                )
                flash("Trustee added.", "success")
            return redirect(url_for("admin_trustees"))

    return render_template("admin/trustee_form.html", mode=mode, trustee=trustee)


@app.route("/admin/trustees/new", methods=["GET", "POST"])
def admin_trustee_new():
    return _trustee_form("new")


@app.route("/admin/trustees/<int:tid>/edit", methods=["GET", "POST"])
def admin_trustee_edit(tid):
    return _trustee_form("edit", tid)


@app.route("/admin/trustees/<int:tid>/delete", methods=["POST"])
def admin_trustee_delete(tid):
    db.execute("DELETE FROM trustees WHERE id = ?", (tid,))
    flash("Trustee deleted.", "success")
    return redirect(url_for("admin_trustees"))


@app.route("/admin/events")
def admin_events():
    rows = db.query("SELECT * FROM events ORDER BY date DESC")
    return render_template("admin/events.html", events=rows)


def _event_form(mode, eid=None):
    event = None
    if mode == "edit":
        row = db.query("SELECT * FROM events WHERE id = ?", (eid,))
        if not row:
            abort(404)
        event = row[0]

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        date = request.form.get("date", "").strip()
        location = request.form.get("location", "").strip()
        description = request.form.get("description", "").strip()
        error = v.validate_event(title, date, location, description)
        if error:
            flash(error, "error")
        else:
            if mode == "edit":
                db.execute(
                    "UPDATE events SET title = ?, date = ?, location = ?, "
                    "description = ? WHERE id = ?",
                    (title, date, location, description, eid),
                )
                flash("Event updated.", "success")
            else:
                db.execute(
                    "INSERT INTO events (title, date, location, description) VALUES (?, ?, ?, ?)",
                    (title, date, location, description),
                )
                flash("Event added.", "success")
            return redirect(url_for("admin_events"))

    return render_template("admin/event_form.html", mode=mode, event=event)


@app.route("/admin/events/new", methods=["GET", "POST"])
def admin_event_new():
    return _event_form("new")


@app.route("/admin/events/<int:eid>/edit", methods=["GET", "POST"])
def admin_event_edit(eid):
    return _event_form("edit", eid)


@app.route("/admin/events/<int:eid>/delete", methods=["POST"])
def admin_event_delete(eid):
    db.execute("DELETE FROM events WHERE id = ?", (eid,))
    flash("Event deleted.", "success")
    return redirect(url_for("admin_events"))


@app.route("/admin/messages")
def admin_messages():
    rows = db.query("SELECT * FROM messages ORDER BY created_at DESC")
    return render_template("admin/messages.html", messages=rows)


@app.route("/admin/messages/<int:mid>/delete", methods=["POST"])
def admin_message_delete(mid):
    db.execute("DELETE FROM messages WHERE id = ?", (mid,))
    flash("Message deleted.", "success")
    return redirect(url_for("admin_messages"))


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "") == "1"
    app.run(debug=debug)
