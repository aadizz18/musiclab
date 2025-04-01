from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask import send_file
from io import BytesIO
from flask import Response

import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure MySQL database URI (use XAMPP's MySQL)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/musiclab"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# User model representing the user table in the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)  # Changed gender to phone
    age = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    instrument = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Gigs(db.Model):
    __tablename__ = 'gig'  # Optional: Specify the table name in your database

    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    audience = db.Column(db.Integer, nullable=False)
    venue = db.Column(db.String(100), nullable=False)
    img1 = db.Column(db.LargeBinary, nullable=True)
    img2 = db.Column(db.LargeBinary, nullable=True)

    # Define the user_id column
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Define the relationship with the User model
    user = db.relationship('User', backref='gigs', lazy=True)

    def __repr__(self):
        return f"<Gig {self.theme}>"

class Collaboration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    work_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    requirement = db.Column(db.String(255), nullable=False)
    artist_profile = db.Column(db.String(255), nullable=True)

    # Add user_id foreign key to associate collaboration with a user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Define the relationship with the User model
    user = db.relationship('User', backref='collaborations', lazy=True)

    def __repr__(self):
        return f"<Collaboration {self.artist_name} - {self.genre}>"

# Define the ContactUs model
class ContactUs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"<ContactUs {self.name} - {self.email}>"

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    user = db.relationship('User', backref='feedback', lazy=True)

    def __repr__(self):
        return f"<Feedback {self.content}>"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/feedback")
def feedback():
    return render_template("feedback.html")


@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    if "email" not in session:
        flash("You need to log in to submit feedback.", "warning")
        return redirect(url_for("login"))

    # Retrieve the logged-in user based on the email in session
    user = User.query.filter_by(email=session["email"]).first()

    # Get the feedback content from the form
    feedback_content = request.form.get("feedback")

    if not feedback_content:
        flash("Please provide some feedback.", "warning")
        return redirect(url_for("feedback"))

    # Create a new Feedback object
    new_feedback = Feedback(content=feedback_content, user_id=user.id)

    try:
        # Add the feedback to the database
        db.session.add(new_feedback)
        db.session.commit()
        flash("Your feedback has been submitted successfully!", "success")
        return redirect(url_for("home"))  # Or you can redirect back to the feedback page
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while submitting your feedback: {e}", "danger")
        return redirect(url_for("feedback"))
 

@app.route("/hire", methods=["GET", "POST"])
def hire():
    if "email" not in session:
        flash("Please log in to upload a gig.", "warning")
        return render_template("hire.html", show_popup=True)  # Flag to show the popup

    if request.method == "POST":
        # Retrieve form data
        theme = request.form.get("theme")
        genre = request.form.get("genre")
        audience = request.form.get("audience")
        venue = request.form.get("venue")

        # Retrieve uploaded files
        img1 = request.files.get("img1")
        img2 = request.files.get("img2")

        # Ensure images are uploaded
        if img1:
            img1_data = img1.read()  # Read the image file as binary data
        else:
            img1_data = None  # If no image uploaded, set to None

        if img2:
            img2_data = img2.read()  # Read the second image file as binary data
        else:
            img2_data = None  # If no second image uploaded, set to None

        # Fetch the current logged-in user from the database
        user = User.query.filter_by(email=session["email"]).first()

        # Create a new Gig object and associate it with the logged-in user
        new_gig = Gigs(
            theme=theme,
            genre=genre,
            audience=int(audience),
            venue=venue,
            img1=img1_data,  # Store the binary data for img1
            img2=img2_data,  # Store the binary data for img2
            user=user  # Directly associate the user object
        )

        try:
            db.session.add(new_gig)
            db.session.commit()
            flash("Gig uploaded successfully!", "success")
            return redirect(url_for("hire"))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
            return redirect(url_for("hire"))

    return render_template("hire.html", show_popup=False)


@app.route('/image/<int:gig_id>/<int:image_num>')
def image(gig_id, image_num):
    # Fetch the gig from the database using gig_id
    gig = Gigs.query.get_or_404(gig_id)

    # Select the correct image based on image_num (either img1 or img2)
    if image_num == 1:
        img_data = gig.img1  # Assuming img1 is a Blob or binary data
    elif image_num == 2:
        img_data = gig.img2  # Assuming img2 is a Blob or binary data
    else:
        return "Image not found", 404

    # Serve the image as a response
    return send_file(BytesIO(img_data), mimetype='image/jpeg')  # Adjust the mimetype as needed


@app.route("/view")
def view():
    # Retrieve all gigs from the database
    gigs = Gigs.query.all()  # This fetches all the gigs from the database
    return render_template("view.html", gigs=gigs)


@app.route("/fill", methods=["GET", "POST"])
def fill():
    if "email" not in session:
        # If the user is not logged in, show the login popup
        return render_template("fill.html", show_popup=True)

    if request.method == "POST":
        # If the user is logged in, process the form submission
        artist_name = request.form['artist_name']
        genre = request.form['genre']
        work_type = request.form['work_type']
        location = request.form['location']
        requirement = request.form['requirement']
        artist_profile = request.form['artist_profile']

        # Example: Add data to database or process the form values
        # Add your own code here to save the collaboration data

        # Flash a success message
        flash('Collaboration submitted successfully!', 'success')

        # Redirect to the same page or any other page you prefer
        return redirect(url_for('colab'))

    return render_template("fill.html", show_popup=False)

@app.route("/colab")
def colab():
    # Retrieve all collaborations from the database, excluding the 'id' column
    collaborations = Collaboration.query.all()
    
    return render_template("colab.html", collaborations=collaborations)


@app.route("/me")
def me():
    # Ensure the user is logged in
    if "email" not in session:
        flash("Please log in to view your profile.", "warning")
        return redirect(url_for("login"))
    
    # Fetch the current logged-in user from the database
    user = User.query.filter_by(email=session["email"]).first()

    # If the user exists, render the page with the user details and their gigs
    if user:
        # Retrieve all gigs uploaded by the logged-in user
        user_gigs = Gigs.query.filter_by(user_id=user.id).all()
        
        # Retrieve all collaborations for the logged-in user (where user_id matches)
        user_collaborations = Collaboration.query.filter_by(user_id=user.id).all()
        
        return render_template("me.html", user=user, gigs=user_gigs, collaborations=user_collaborations)
    
    # If no user is found, redirect to login page
    flash("User not found. Please log in again.", "warning")
    return redirect(url_for("login"))



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")  # Changed 'gender' to 'phone'
        age = request.form.get("age")
        type = request.form.get("type")  # Corrected 'Type' to 'type'
        genre = request.form.get("genre")
        instrument = request.form.get("instrument")  # Corrected 'Instrument' to 'instrument'
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Password confirmation check
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered", "danger")
            return redirect(url_for("register"))

        # Creating a new user object, and passing phone instead of gender
        new_user = User(
            name=name, 
            email=email, 
            phone=phone,  # Store the phone number
            age=int(age),
            type=type, 
            genre=genre, 
            instrument=instrument,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password", "danger")
            return redirect(url_for("login"))

        # Log the user in by saving the email in the session
        session["email"] = user.email
        flash("Login successful!", "success")

        # Get the referring page (the page the user was on before logging in)
        referrer = request.referrer
        
        # If the referrer is None (user directly visited login page), redirect to home page
        if not referrer or "login" in referrer or "logout" in referrer:
            referrer = url_for("home")  # Redirect to home page if the referrer is invalid or None

        # Redirect the user back to the page they came from (or home if no valid referrer)
        return redirect(referrer)
    
    return render_template("login.html")



@app.route("/logout")
def logout():
    # Get the referring page (the page the user was on before they logged out)
    referrer = request.referrer or url_for("home")  # Default to home page if referrer is None
    
    # Remove the email from the session to log the user out
    session.pop("email", None)
    
    # Flash message to notify the user of successful logout
    flash("You have been logged out.", "info")
    
    # Redirect the user back to the page they logged out from (or home if no referrer)
    return redirect(referrer)

@app.route("/profile")
def profile():
    if "email" in session:
        user = User.query.filter_by(email=session["email"]).first()
        return render_template("profile.html", user=user)
    flash("Please log in to view your profile.", "warning")
    return redirect(url_for("login"))

@app.route("/apply/<int:gig_id>")
def apply(gig_id):
    # Your application logic here
    # For example, saving the application to the database
    flash(f"Applied for gig {gig_id}!", "success")
    return redirect(url_for("view"))  # Redirect to the view page after applying
@app.route("/submit_collaboration", methods=["POST"])
def submit_collaboration():
    if request.method == "POST":
        # Retrieve form data
        artist_name = request.form.get("artist_name")
        genre = request.form.get("genre")
        work_type = request.form.get("work_type")
        location = request.form.get("location")
        requirement = request.form.get("requirement")
        artist_profile = request.form.get("artist_profile")

        # Retrieve the current logged-in user from the session
        user = User.query.filter_by(email=session["email"]).first()

        # Create a new Collaboration object and associate it with the logged-in user
        new_collab = Collaboration(
            artist_name=artist_name,
            genre=genre,
            work_type=work_type,
            location=location,
            requirement=requirement,
            artist_profile=artist_profile,
            user_id=user.id  # Link collaboration to the logged-in user
        )

        # Add the new collaboration to the database and commit
        try:
            db.session.add(new_collab)
            db.session.commit()
            flash("Collaboration submitted successfully!", "success")
            return redirect(url_for("home"))  # Redirect back to home after submission
        except Exception as e:
            db.session.rollback()  # Rollback in case of an error
            flash(f"An error occurred: {e}", "danger")
            return redirect(url_for("fill"))  # Redirect back to the form in case of an error


@app.route("/contactus", methods=["GET", "POST"])
def contactus():
    if request.method == "POST":
        # Retrieve form data
        name = request.form['fullname']
        email = request.form['email']
        message = request.form['message']

        # Check if all fields are filled
        if not name or not email or not message:
            flash("Please fill in all the fields.", "danger")
            return redirect(url_for('contactus'))

        # Create a new ContactUs record
        new_contact = ContactUs(
            name=name,
            email=email,
            message=message
        )

        # Add to the database and commit the transaction
        try:
            db.session.add(new_contact)
            db.session.commit()
            flash("Your message has been sent successfully!", "success")
            return redirect(url_for('contactus'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
            return redirect(url_for('contactus'))

    return render_template("contactus.html")

@app.route("/delete_gig/<int:gig_id>", methods=["POST"])
def delete_gig(gig_id):
    if "email" not in session:
        flash("Please log in to perform this action.", "warning")
        return redirect(url_for("login"))
    
    gig = Gigs.query.get_or_404(gig_id)
    
    # Verify the gig belongs to the current user
    user = User.query.filter_by(email=session["email"]).first()
    if gig.user_id != user.id:
        flash("You don't have permission to delete this gig.", "danger")
        return redirect(url_for("me"))
    
    try:
        db.session.delete(gig)
        db.session.commit()
        flash("Gig deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {e}", "danger")
    
    return redirect(url_for("me"))

@app.route("/forgetpass", methods=["GET", "POST"])
def forgetpass():
    if request.method == "POST":
        email = request.form.get("email")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        # Check if passwords match
        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("forgetpass"))

        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("No account found with that email.", "danger")
            return redirect(url_for("forgetpass"))

        # Update the password
        hashed_password = generate_password_hash(new_password)
        user.password = hashed_password
        db.session.commit()

        flash("Password updated successfully! You can now login with your new password.", "success")
        return redirect(url_for("login"))

    return render_template("forgetpass.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure the database schema is created
    app.run(debug=True, port=8000, use_reloader=False)

