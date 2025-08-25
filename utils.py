from flask_mail import Message
from flask import url_for, current_app
import re

def send_email(to, subject, template):
    from app import mail
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)

def send_verification_email(user):
    token = user.get_verification_token()
    verify_url = url_for('verify_email', token=token, _external=True)
    
    html = f"""
    <h1>Email Verification</h1>
    <p>Please click the link below to verify your email address:</p>
    <a href="{verify_url}">Verify Email</a>
    <p>This link will expire in 1 hour.</p>
    """
    
    send_email(user.email, 'Verify Your Email', html)

def send_password_reset_email(user):
    token = user.get_reset_token()
    reset_url = url_for('reset_password', token=token, _external=True)
    
    html = f"""
    <h1>Password Reset Request</h1>
    <p>You requested to reset your password. Click the link below:</p>
    <a href="{reset_url}">Reset Password</a>
    <p>This link will expire in 1 hour.</p>
    <p>If you didn't request this, please ignore this email.</p>
    """
    
    send_email(user.email, 'Password Reset Request', html)

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_strong_password(password):
    if len(password) < 8:
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.islower() for char in password):
        return False
    if not any(char.isdigit() for char in password):
        return False
    return True