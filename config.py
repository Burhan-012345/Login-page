import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email configuration for Gmail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'ahmedburhan4834@gmail.com'
    MAIL_PASSWORD = 'cnzwlrvuqvskella'  # Your app password
    MAIL_DEFAULT_SENDER = 'ahmedburhan4834@gmail.com'
    
    # Reset token expiration (1 hour)
    RESET_TOKEN_EXPIRATION = 3600