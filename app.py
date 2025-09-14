from flask import Flask, request, render_template, redirect, url_for, session, send_from_directory
from models import db, User, Files
from werkzeug.utils import secure_filename
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv

# --- App Configuration ---
load_dotenv()
app = Flask(__name__)
# 🚩 Using a secure key for sessions
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key') 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# 🚩 Fix: Cloudinary Configuration - using correct variable names
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

with app.app_context():
    db.create_all()

# --- Routes ---
@app.route("/")
def Login_page():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        Username1 = request.form.get("username1")
        Password1 = request.form.get("password1")
        if not Username1 or not Password1:
            return "Fields should not remain empty"
        user = User.query.filter_by(username=Username1).first()
        if user and user.password == Password1:
            session['user_id'] = user.id
            return redirect(url_for("dashboard"))
        else:
            return "Invalid credentials"
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    return render_template("signup.html")

@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        Username = request.form.get("username")
        Fullname = request.form.get("fullname")
        Email = request.form.get("email")
        Password = request.form.get("password")
        Cpassword = request.form.get("cpassword")
        if not Username or not Fullname or not Password or not Cpassword:
            return "Fields should not be empty"
        if Password != Cpassword:
            return "Passwords Should Match"
        
        new_user = User(username=Username, fullName=Fullname, email=Email, password=Password)
        db.session.add(new_user)
        db.session.commit()
        return f"Signup, succesful! Welcome, {Fullname}"
    return "Please submit the form!"

@app.route("/Upload", methods=["POST", "GET"])
def fileUpload_page():
    return render_template("Upload_form.html")

@app.route("/upload_file", methods=["POST", "GET"])
def file_Upload():
    if request.method == "POST":
        file_to_upload = request.files["File"]
        if not file_to_upload:
            return "File not found"

        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))

        try:
            result = cloudinary.uploader.upload(file_to_upload)
            public_id = result.get('public_id')
            file_url = result.get('secure_url')
            
            new_file = Files(filename=public_id, url=file_url, user_id=user_id) 
            db.session.add(new_file)
            db.session.commit()
            
            return redirect(url_for('dashboard'))

        except Exception as e:
            return f"An error occurred: {e}"
            
    return render_template("Upload_form.html")

@app.route("/dashboard", methods=["GET"])
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login')) 

    files_list = Files.query.filter_by(user_id=user_id).all()
    return render_template("dashboard.html", files=files_list)

@app.route("/view_file/<filename>")
def view_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/download_file/<filename>")
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)