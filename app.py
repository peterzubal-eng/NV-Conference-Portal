# Import necessary Flask tools for rendering templates, handling form data, redirects, and user sessions.
from flask import Flask, render_template, request, redirect, url_for, session
# Import SQLAlchemy to connect to and manage our SQL database easily with Python objects.
from flask_sqlalchemy import SQLAlchemy

# Initialize the Flask application.
app = Flask(__name__)
# Set a secret key to sign and secure session cookies (like keeping the admin logged in).
app.secret_key = "secret123"
# Tell Flask to look for a local SQLite database file named 'database.db'.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# Disable a legacy feature we don't need, which saves system memory.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Bind the database manager to our Flask application.
db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

# =========================================================================
# DATABASE MODELS
# =========================================================================

# This blueprint defines the 'Event' table structure in our database.
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)   # Unique identifier for each event
    title = db.Column(db.String(100))               # Title of the conference
    event_date = db.Column(db.String(20))           # Date of the conference
    location = db.Column(db.String(100))            # Physical venue address


# This blueprint defines the 'Registration' table structure for storing attendee data.
class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)   # Unique identifier for each registration entry
    first_name = db.Column(db.String(50))           # Attendee's first name
    surname = db.Column(db.String(50))              # Attendee's last name
    company = db.Column(db.String(100))             # Workplace or affiliation
    email = db.Column(db.String(120))               # Attendee's primary email contact
    phone = db.Column(db.String(30))                # Contact phone number
    conference_day = db.Column(db.String(100))      # Selected session track/time slot
    consent = db.Column(db.Boolean)                 # True/False value tracking data privacy consent
    status = db.Column(db.String(20), default="Confirmed") # Default registration status
    # Links each registration directly to an Event ID (Foreign Key relationship).
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))


# =========================================================================
# APPLICATION ROUTES
# =========================================================================

# Homepage route: fetches the event details from the database and shows the main page.
@app.route("/")
def home():
    event = Event.query.first() # Grab the first event entry available
    return render_template("index.html", event=event)


# Registration form route: handles showing the form (GET) and processing user inputs (POST).
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        # Create a new registration database record using data typed into the HTML inputs
        registration = Registration(
            first_name=request.form["firstname"],
            surname=request.form["surname"],
            company=request.form["company"],
            email=request.form["email"],
            phone=request.form["phone"],
            conference_day=request.form["session"],
            consent=True, # Hardcoded as True assuming front-end validation passed
            event_id=1    # Tied directly to our primary event ID
        )
        db.session.add(registration) # Stage the entry for saving
        db.session.commit()          # Save permanently to database.db
        return redirect(url_for("confirmation")) # Send user to the success screen
    
    return render_template("register.html")


# Success confirmation route: renders a simple landing thank-you page after registration.
@app.route("/confirmation")
def confirmation():
    return render_template("confirmation.html")


# Admin login route: authenticates admin credentials and opens up a secure session cookie.
@app.route("/login", methods=["GET","POST"])
def login():
    error = None
    if request.method == "POST":
        # Check if login inputs match the hardcoded administrator credentials
        if request.form["username"] == "admin" and request.form["password"] == "password":
            session["admin"] = True # Remember that the user is securely logged in
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid credentials. Please try again." # Set alert message for wrong login
    return render_template("admin_login.html", error=error)


# Admin dashboard route: displays all current attendees in a structured grid layout.
@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect(url_for("login")) # Kick unauthorized users back to login
    
    registrations = Registration.query.all() # Fetch all attendee records from database
    return render_template("dashboard.html", registrations=registrations)


# Attendee detail route: displays a deep-dive comprehensive look into a specific profile card.
@app.route("/registration/<int:id>")
def detail(id):
    if "admin" not in session:
        return redirect(url_for("login"))
    
    registration = Registration.query.get_or_404(id) # Fetch data by ID or throw a 404 error page
    return render_template("registration_detail.html", registration=registration)


# Edit profile route: opens up a modification screen to let the admin adjust email or phone records.
@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):
    if "admin" not in session:
        return redirect(url_for("login"))
    
    registration = Registration.query.get_or_404(id)
    if request.method == "POST":
        # Overwrite current database values with the newly typed form values
        registration.email = request.form["email"]
        registration.phone = request.form["phone"]
        db.session.commit() # Save updates safely
        return redirect(url_for("dashboard"))
        
    return render_template("edit_registration.html", registration=registration)


# Cancel ticket route: flips an active profile's status flag value to "Cancelled".
@app.route("/cancel/<int:id>")
def cancel(id):
    if "admin" not in session:
        return redirect(url_for("login"))
    
    registration = Registration.query.get_or_404(id)
    registration.status = "Cancelled" # Change the text status string inside database row
    db.session.commit()
    return redirect(url_for("dashboard"))


# Logout route: fully clears out session tracking data cookies to sign the administrator out.
@app.route("/logout")
def logout():
    session.clear() # Delete everything inside session memory storage
    return redirect(url_for("home"))


# =========================================================================
# APP INITIALIZATION
# =========================================================================

if __name__ == "__main__":
    with app.app_context():
        db.create_all() # Automatically generate empty database tables if they don't exist yet
        
        # Seed data: automatically populate initial conference metrics if the database is brand new.
        if Event.query.count() == 0:
            event = Event(
                title="The AI Conference 2026",
                event_date="10 August 2026",
                location="Dublin Convention Centre"
            )
            db.session.add(event)
            db.session.commit()
            
    app.run(host="0.0.0.0", port=5000) # Run the website online