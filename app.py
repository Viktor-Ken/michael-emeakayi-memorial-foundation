from flask import Flask, render_template, request, redirect, url_for, flash, abort

import db

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-key-before-deploying"
db.init_app(app)


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

        if not name or not email or not message:
            flash("Please fill in your name, email and message.", "error")
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
        if not name or not role:
            flash("Name and role are required.", "error")
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
        if not title or not date:
            flash("Title and date are required.", "error")
        else:
            if mode == "edit":
                db.execute(
                    "UPDATE events SET title = ?, date = ?, location = ?, description = ? WHERE id = ?",
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
    app.run(debug=True)