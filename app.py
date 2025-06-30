from flask import Flask, request, render_template, redirect, session, flash
from PIL import Image
import os
from model_utils import AI_Models
import uuid
import time, glob
from user import db, bcrypt, User
import re
from validate_email_address import validate_email

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'hager_melook***'

db.init_app(app)
bcrypt.init_app(app)

with app.app_context():
    # create all the tables in the database if not exist
    db.create_all()

UPLOAD_FOLDER = "static/uploaded_images"
os.makedirs(UPLOAD_FOLDER, exist_ok = True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    # to allow only the authenticated users to use this feature
    if 'user_id' not in session:
        flash("🔒 Please log in to analyze your image.")
        return redirect('/register')
    
    # automatic removal of the uploaded images
    for f in glob.glob(os.path.join(UPLOAD_FOLDER, "*.jpg")):
        if time.time() - os.path.getmtime(f) > 600:
            os.remove(f)

    if request.method == 'GET':
        return render_template('analyze.html')

    if 'image' not in request.files:
        return render_template('analyze.html', result = "No image uploaded")
    image_file = request.files['image']

    if image_file.filename == '':
        return render_template('analyze.html', result="No image selected")
    
    if image_file and allowed_file(image_file.filename):
        try:
            img = Image.open(image_file.stream)
            img.verify()  # Verifies that it’s an actual image
            image_file.stream.seek(0)  # Reset stream position after verify
        except Exception:
            return render_template('analyze.html', result="Invalid image file")
    else:
        return render_template('analyze.html', result="Invalid file type")
    
    # Create a unique image file name and these help in handling the concurrent user access
    unique_filename = f"{uuid.uuid4().hex}.jpg" 
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
    image_file.save(filepath)

    image = Image.open(filepath)
    ai = AI_Models(image)

    if not ai.classify():
        return render_template('analyze.html', result = "No pets found in the image", image_url = unique_filename)

    boxes = ai.detect()
    mask = ai.segment()
    mask_b64 = ai.mask_to_base64(mask)

    return render_template(
        "analyze.html",
        result = "Pet detected",
        classification = ai.cls_name,
        boxes = boxes,
        mask_base64 = mask_b64,
        image_url = unique_filename
    )

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect('/profile')

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']

        if password != confirm:
            flash('Passwords do not match')
            return redirect('/register')

        if User.query.filter_by(email = email).first():
            flash('Email already registered')
            return redirect('/register')
        
        if not validate_email(email):
            flash("Please enter a valid email address.")
            return redirect('/register')

        user = User(username = username, email = email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id

        flash('Registered successfully!')
        return redirect('/profile')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect('/profile')
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email = email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash(f"Welcome, {user.username}!")
            return redirect('/profile')
        else:
            flash("Invalid email or password.")
            return redirect('/login')
        
    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/register')
    # deprecated
    # user = User.query.get(session['user_id'])
    user = db.session.get(User, session['user_id'])
    return render_template('profile.html', user = user)
        
@app.route('/upload-photo', methods=['POST'])
def upload_photo():
    if 'user_id' not in session:
        return redirect('/register')
    
    user = db.session.get(User, session['user_id'])
    if not user:
        return redirect('/register')
    
    image_file = request.files.get('profile_photo')

    if image_file.filename == '':
        flash('No image selected.')
        return redirect('/profile')
    
    if image_file and allowed_file(image_file.filename):
        try:
            img = Image.open(image_file.stream)
            img.verify()  # Verifies that it’s an actual image
            image_file.stream.seek(0)  # Reset stream position after verify
        except Exception:
            flash('Invalid image type.')
            return redirect('/profile')
    else:
        flash('Invalid file type.')
        return redirect('/profile')
    
    if image_file and image_file.filename != '':
        filename = f"{uuid.uuid4().hex}.jpg"
        path = os.path.join('static', 'profile_pics', filename)
        image_file.save(path)

        #delete old image (unless it's the default)
        if user.profile_image != 'default.png':
            try:
                os.remove(os.path.join('static', 'profile_pics', user.profile_image))
            except FileNotFoundError:
                pass

        user.profile_image = filename
        db.session.commit()
        flash('Profile photo updated.')
    else:
        flash('No image selected.')
    return redirect('/profile')

@app.route('/logout')
def logout():
    if 'user_id' not in session:
        return redirect('/register')
    session.clear()
    return render_template('logout.html')

# to make sure that the user can't logout and return to his profile
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "-1"
    return response

if __name__ == '__main__':
    app.run(debug=True)