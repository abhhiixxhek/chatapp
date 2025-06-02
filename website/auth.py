from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import login_user, logout_user, login_required
from . import db
from .__init__ import User
from cloudinary import uploader
from cloudinary.utils import cloudinary_url

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['POST', 'GET'])
def signup_post():
    if request.method == 'POST':
        print(f"[SIGNUP] Received email: {request.form.get('email')}")
        print(f"[SIGNUP] Received name: {request.form.get('name')}")
        print(f"[SIGNUP] Received password (length): {len(request.form.get('password')) if request.form.get('password') else 'None'}")
        error = None
        thumbnail_url1 = None
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        image = request.files['image']
        if image:
            upload_result = uploader.upload(image)
            # image = Cloud.CloudinaryImage(request.form.get('image'))
            thumbnail_url1, options = cloudinary_url(
                        upload_result['public_id'],
                        crop="fill",)
        else:
            thumbnail_url1 = 'https://png.pngitem.com/pimgs/s/150-1503945_transparent-user-png-default-user-image-png-png.png'                
        
        if not password or not email or not name:
            error = "Invalid Credentials. Please try again."
            print(f"[SIGNUP] Error condition: {error}")
            return render_template("/auth/login-register.html", error=error)

        if User.query.filter_by(name=name).count() == 1:
            error = "Name already taken. Please try again."
            print(f"[SIGNUP] Error condition: {error}")
            return render_template("/auth/login-register.html", error=error)

        if User.query.filter_by(email=email).count() == 1:
            error = "Email already taken. Please try again."
            print(f"[SIGNUP] Error condition: {error}")
            return render_template("/auth/login-register.html", error=error)

        u = User()
        u.name = name
        u.email = email
        u.image = thumbnail_url1
        u.set_password(password)

        print(f"[SIGNUP] Creating User: name='{u.name}', email='{u.email}', image_url='{u.image}'")
        print(f"[SIGNUP] Is password_hash set before commit? {'Yes' if u.password_hash else 'No'}")

        # session['username'] = name # Removed as Flask-Login handles user session
        db.session.add(u)
        db.session.commit()

        print(f"[SIGNUP] User {u.name} committed to database with ID: {u.id}")
        # Verify user from DB immediately
        committed_user = User.query.filter_by(email=u.email).first()
        if committed_user:
            print(f"[SIGNUP] Verified user from DB: id={committed_user.id}, name='{committed_user.name}', hash='{committed_user.password_hash[:20]}...'")
        else:
            print(f"[SIGNUP] CRITICAL: User not found in DB immediately after commit with email {u.email}!")

        return render_template("/auth/login-register.html")
    else:
        return render_template("/auth/login-register.html")


@auth.route('/login', methods=['POST'])
def login_post():
    print(f"[LOGIN] Attempting login for name: {request.form.get('name')}")
    print(f"[LOGIN] Password provided (length): {len(request.form.get('password')) if request.form.get('password') else 'None'}")
    error = None
    name = request.form.get('name')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    if not name or not password:
        error = "Missing Data"
        print(f"[LOGIN] Error condition: {error}")
        return render_template("/auth/login-register.html", error=error)

    user = User.query.filter_by(name=name).first()

    if user:
        print(f"[LOGIN] User found in DB: id={user.id}, name='{user.name}', hash='{user.password_hash[:20]}...'")
    else:
        print(f"[LOGIN] User '{name}' NOT found in DB.")

    if user is None or not user.check_password(password):
        error = "Please check your login details and try again."
        if user: # Implies password check failed
             print(f"[LOGIN] Password check FAILED for user '{name}'.")
        # If user is None, the "NOT found in DB" message is already printed
        print(f"[LOGIN] Error condition: {error}")
        return render_template("/auth/login-register.html", error=error)

    # This part is reached only if user exists and password check was successful
    print(f"[LOGIN] Password check successful for user '{name}'.")

    session.pop('username', None)
    login_user(user, remember=remember)
    return redirect(url_for('views.chat'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    # Clear custom session variables that might have been set
    session.pop('username', None) # For any legacy direct setting
    session.pop('USERNAME', None) # For any legacy direct setting (uppercase)
    session.pop('name', None)     # This was used for workspace name in views.py
    session.pop('imageid', None)  # This was used for image id in views.py
    return render_template('/auth/login-register.html')
