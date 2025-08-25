# Compatibility fix for Werkzeug import issue
try:
    from werkzeug.urls import url_decode
except ImportError:
    from werkzeug.utils import url_decode

import sys
if 'flask_login.utils' in sys.modules:
    sys.modules['flask_login.utils'].url_decode = url_decode

# Now import the regular Flask components
import os
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_mail import Mail
from models import db, User
from utils import send_verification_email, send_password_reset_email, is_valid_email, is_strong_password
from config import Config
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
mail = Mail(app)

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/test')
def test_route():
    return "Flask is working! Now go to <a href='/login'>login page</a>"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            flash('Please fill all fields', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        if not is_valid_email(email):
            flash('Please enter a valid email address', 'danger')
            return render_template('register.html')
        
        if not is_strong_password(password):
            flash('Password must be at least 8 characters with uppercase, lowercase, and numbers', 'danger')
            return render_template('register.html')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html')
        
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Send verification email
            send_verification_email(user)
            flash('Registration successful! Please check your email to verify your account.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration', 'danger')
    
    return render_template('register.html')

@app.route('/verify_email/<token>')
def verify_email(token):
    user = User.verify_verification_token(token)
    if user is None:
        flash('Invalid or expired verification token', 'danger')
        return redirect(url_for('login'))
    
    user.email_verified = True
    db.session.commit()
    flash('Email verified successfully! You can now log in.', 'success')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.email_verified:
                flash('Please verify your email before logging in', 'warning')
                return render_template('login.html')
            
            login_user(user, remember=bool(remember))
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            send_password_reset_email(user)
            flash('Password reset instructions have been sent to your email', 'info')
            return redirect(url_for('login'))
        else:
            flash('If that email exists, instructions have been sent', 'info')
            return redirect(url_for('login'))
    
    return render_template('reset_request.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('reset_password_request'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('reset_password.html', token=token)
        
        if not is_strong_password(password):
            flash('Password must be at least 8 characters with uppercase, lowercase, and numbers', 'danger')
            return render_template('reset_password.html', token=token)
        
        user.set_password(password)
        db.session.commit()
        
        flash('Your password has been reset successfully!', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)

# Create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # For Termux, use 0.0.0.0 to allow access from other devices on the network
    app.run(host='0.0.0.0', port=5000, debug=True)
