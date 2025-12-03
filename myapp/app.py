from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "foundation_secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///foundation.db"
db = SQLAlchemy(app)

# -------------------------
# Database Models
# -------------------------
class Trustee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200), nullable=True)  # image filename relative to static/images/

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(200), nullable=True)  # event banner filename relative to static/images/

# -------------------------
# Routes
# -------------------------
@app.route("/")
def home():
    events = Event.query.all()
    return render_template("index.html", events=events)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/initiatives")
def initiatives():
    return render_template("initiatives.html")

@app.route("/trustees")
def trustees():
    trustees = Trustee.query.all()
    return render_template("trustees.html", trustees=trustees)

@app.route("/events")
def events():
    events = Event.query.all()
    return render_template("events.html", events=events)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        flash("Thank you for contacting us — we will respond shortly.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")

@app.route("/donate")
def donate():
    return render_template("donate.html")

# Inject current_year into templates
@app.context_processor
def inject_now():
    return {"current_year": datetime.utcnow().year}

# -------------------------
# Seed Data with Images (run once)
# -------------------------
def seed_data():
    if Trustee.query.count() == 0:
        trustees = [
            Trustee(
                name="Hope Chizoba Emeakayi Okafor",
                role="Founder & Chairperson",
                bio="Researcher and community advocate based in the United Kingdom, leading the vision and coordination of the Foundation.",
                image="trustees/hope.jpg"
            ),
            Trustee(
                name="Kenneth Okwuchukwu Emeakayi",
                role="Trustee & Patron",
                bio="A respected elder statesman and community leader with a long history of public service, mentorship, and advocacy.",
                image="trustees/kenneth.jpg"
            ),
            Trustee(
                name="Chisom Francisca Emeakayi",
                role="Trustee & Secretary",
                bio="Responsible for administrative coordination and record-keeping of all Foundation activities and meetings.",
                image="trustees/chisom.jpg"
            ),
            Trustee(
                name="Angelina Mmachukwu Emeakayi",
                role="Trustee, Matron & Wife of the Late High Chief Michael Emeakayi",
                bio="A pillar of strength in the Umuohi community and lifelong partner to the late Chief, ensuring the Foundation remains true to its founding values.",
                image="trustees/angelina.jpg"
            ),
            Trustee(
                name="Victor Nnamdi Emeakayi",
                role="Trustee & IT Programme Coordinator",
                bio="Leads the Foundation’s IT Skills Training Programme, supporting digital literacy initiatives and the development of the IT training centre.",
                image="trustees/victor.jpg"
            ),
        ]
        db.session.add_all(trustees)
        db.session.commit()

    if Event.query.count() == 0:
        event = Event(
            title="Annual Harvest, Award Presentation & Fundraising Event",
            description="A unified celebration of education, agriculture, and community impact. Students, educators, families, and global supporters come together to honour excellence, distribute scholarships and harvests, and raise funds for future programme cycles.",
            date="December 2025",
            image="events/annual-harvest.jpg"
        )
        db.session.add(event)
        db.session.commit()

# -------------------------
# Run Application
# -------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True)
