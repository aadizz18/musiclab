from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
import pymysql

pymysql.install_as_MySQLdb()

# Initialize extensions
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'

    # Configure database
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/musiclab"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize extensions
    db.init_app(app)

    # Create tables
    with app.app_context():
        db.create_all()

    # Register blueprints
    app.register_blueprint(main_bp)

    return app

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    instrument = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Gigs(db.Model):
    __tablename__ = 'gig'
    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    audience = db.Column(db.Integer, nullable=False)
    venue = db.Column(db.String(100), nullable=False)
    img1 = db.Column(db.LargeBinary, nullable=True)
    img2 = db.Column(db.LargeBinary, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='gigs', lazy=True)

class Collaboration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    work_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    requirement = db.Column(db.String(255), nullable=False)
    artist_profile = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='collaborations', lazy=True)

class ContactUs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(500), nullable=False)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='feedback', lazy=True)

# Create blueprint
main_bp = Blueprint('main', __name__)

# Routes
@main_bp.route("/")
def home():
    return render_template("home.html")

@main_bp.route("/about")
def about():
    return render_template("about.html")

@main_bp.route("/feedback")
def feedback():
    return render_template("feedback.html")

@main_bp.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    if "email" not in session:
        flash("You need to log in to submit feedback.", "warning")
        return redirect(url_for("main.login"))

    user = User.query.filter_by(email=session["email"]).first()
    feedback_content = request.form.get("feedback")

    if not feedback_content:
        flash("Please provide some feedback.", "warning")
        return redirect(url_for("main.feedback"))

    new_feedback = Feedback(content=feedback_content, user_id=user.id)
    try:
        db.session.add(new_feedback)
        db.session.commit()
        flash("Feedback submitted successfully!", "success")
        return redirect(url_for("main.home"))
    except Exception as e:
        db.session.rollback()
        flash(f"Error submitting feedback: {e}", "danger")
        return redirect(url_for("main.feedback"))

@main_bp.route("/hire", methods=["GET", "POST"])
def hire():
    if "email" not in session:
        flash("Please log in to upload a gig.", "warning")
        return render_template("hire.html", show_popup=True)

    if request.method == "POST":
        theme = request.form.get("theme")
        genre = request.form.get("genre")
        audience = request.form.get("audience")
        venue = request.form.get("venue")
        img1 = request.files.get("img1")
        img2 = request.files.get("img2")

        img1_data = img1.read() if img1 else None
        img2_data = img2.read() if img2 else None

        user = User.query.filter_by(email=session["email"]).first()

        new_gig = Gigs(
            theme=theme,
            genre=genre,
            audience=int(audience),
            venue=venue,
            img1=img1_data,
            img2=img2_data,
            user=user
        )

        try:
            db.session.add(new_gig)
            db.session.commit()
            flash("Gig uploaded successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error uploading gig: {e}", "danger")

        return redirect(url_for("main.hire"))

    return render_template("hire.html", show_popup=False)

@main_bp.route('/image/<int:gig_id>/<int:image_num>')
def image(gig_id, image_num):
    gig = Gigs.query.get_or_404(gig_id)
    img_data = gig.img1 if image_num == 1 else gig.img2 if image_num == 2 else None
    if not img_data:
        return "Image not found", 404
    return send_file(BytesIO(img_data), mimetype='image/jpeg')

@main_bp.route("/view")
def view():
    gigs = Gigs.query.all()
    return render_template("view.html", gigs=gigs)

@main_bp.route("/fill", methods=["GET", "POST"])
def fill():
    if "email" not in session:
        return render_template("fill.html", show_popup=True)

    if request.method == "POST":
        artist_name = request.form['artist_name']
        genre = request.form['genre']
        work_type = request.form['work_type']
        location = request.form['location']
        requirement = request.form['requirement']
        artist_profile = request.form['artist_profile']

        user = User.query.filter_by(email=session["email"]).first()

        new_collab = Collaboration(
            artist_name=artist_name,
            genre=genre,
            work_type=work_type,
            location=location,
            requirement=requirement,
            artist_profile=artist_profile,
            user_id=user.id
        )

        try:
            db.session.add(new_collab)
            db.session.commit()
            flash("Collaboration submitted!", "success")
            return redirect(url_for("main.home"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error submitting collaboration: {e}", "danger")
            return redirect(url_for("main.fill"))

    return render_template("fill.html", show_popup=False)

@main_bp.route("/colab")
def colab():
    collaborations = Collaboration.query.all()
    return render_template("colab.html", collaborations=collaborations)

@main_bp.route("/me")
def me():
    if "email" not in session:
        flash("Please log in.", "warning")
        return redirect(url_for("main.login"))
    
    user = User.query.filter_by(email=session["email"]).first()
    if user:
        user_gigs = Gigs.query.filter_by(user_id=user.id).all()
        user_collaborations = Collaboration.query.filter_by(user_id=user.id).all()
        return render_template("me.html", user=user, gigs=user_gigs, collaborations=user_collaborations)
    
    flash("User not found.", "danger")
    return redirect(url_for("main.login"))

@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        age = request.form.get("age")
        type = request.form.get("type")
        genre = request.form.get("genre")
        instrument = request.form.get("instrument")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords don't match!", "danger")
            return redirect(url_for("main.register"))

        hashed_password = generate_password_hash(password)
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered!", "danger")
            return redirect(url_for("main.register"))

        new_user = User(
            name=name,
            email=email,
            phone=phone,
            age=int(age),
            type=type,
            genre=genre,
            instrument=instrument,
            password=hashed_password
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("main.login"))
        except Exception as e:
            db.session.rollback()
            flash(f"Registration failed: {e}", "danger")
            return redirect(url_for("main.register"))

    return render_template("register.html")

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash("Invalid credentials!", "danger")
            return redirect(url_for("main.login"))

        session["email"] = user.email
        flash("Login successful!", "success")
        return redirect(url_for("main.home"))

    return render_template("login.html")

@main_bp.route("/logout")
def logout():
    session.pop("email", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("main.home"))

@main_bp.route("/profile")
def profile():
    if "email" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("main.login"))
    
    user = User.query.filter_by(email=session["email"]).first()
    return render_template("profile.html", user=user)

@main_bp.route("/apply/<int:gig_id>")
def apply(gig_id):
    flash(f"Applied for gig {gig_id}!", "success")
    return redirect(url_for("main.view"))

@main_bp.route("/submit_collaboration", methods=["POST"])
def submit_collaboration():
    if "email" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("main.login"))

    artist_name = request.form.get("artist_name")
    genre = request.form.get("genre")
    work_type = request.form.get("work_type")
    location = request.form.get("location")
    requirement = request.form.get("requirement")
    artist_profile = request.form.get("artist_profile")

    user = User.query.filter_by(email=session["email"]).first()

    new_collab = Collaboration(
        artist_name=artist_name,
        genre=genre,
        work_type=work_type,
        location=location,
        requirement=requirement,
        artist_profile=artist_profile,
        user_id=user.id
    )

    try:
        db.session.add(new_collab)
        db.session.commit()
        flash("Collaboration submitted!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "danger")

    return redirect(url_for("main.fill"))

@main_bp.route("/contactus", methods=["GET", "POST"])
def contactus():
    if request.method == "POST":
        name = request.form['fullname']
        email = request.form['email']
        message = request.form['message']

        if not all([name, email, message]):
            flash("Please fill all fields.", "warning")
            return redirect(url_for("main.contactus"))

        new_contact = ContactUs(
            name=name,
            email=email,
            message=message
        )

        try:
            db.session.add(new_contact)
            db.session.commit()
            flash("Message sent!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {e}", "danger")

        return redirect(url_for("main.contactus"))

    return render_template("contactus.html")

@main_bp.route("/delete_gig/<int:gig_id>", methods=["POST"])
def delete_gig(gig_id):
    if "email" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("main.login"))

    gig = Gigs.query.get_or_404(gig_id)
    user = User.query.filter_by(email=session["email"]).first()

    if gig.user_id != user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("main.me"))

    try:
        db.session.delete(gig)
        db.session.commit()
        flash("Gig deleted!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "danger")

    return redirect(url_for("main.me"))

@main_bp.route("/forgetpass", methods=["GET", "POST"])
def forgetpass():
    if request.method == "POST":
        email = request.form.get("email")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if new_password != confirm_password:
            flash("Passwords don't match!", "danger")
            return redirect(url_for("main.forgetpass"))

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Email not found!", "danger")
            return redirect(url_for("main.forgetpass"))

        user.password = generate_password_hash(new_password)
        db.session.commit()
        flash("Password updated! Please login.", "success")
        return redirect(url_for("main.login"))

    return render_template("forgetpass.html")

# Create app instance
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
