from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import bcrypt
from itsdangerous import URLSafeTimedSerializer as Serializer
from config import Config

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def get_reset_token(self, expires_sec=3600):
        s = Serializer(Config.SECRET_KEY)
        return s.dumps({'user_id': self.id}, salt='password-reset-salt')
    
    @staticmethod
    def verify_reset_token(token, expires_sec=3600):
        s = Serializer(Config.SECRET_KEY)
        try:
            data = s.loads(token, salt='password-reset-salt', max_age=expires_sec)
            user_id = data['user_id']
        except:
            return None
        return User.query.get(user_id)
    
    def get_verification_token(self, expires_sec=3600):
        s = Serializer(Config.SECRET_KEY)
        return s.dumps({'user_id': self.id, 'email': self.email}, salt='email-verify-salt')
    
    @staticmethod
    def verify_verification_token(token, expires_sec=3600):
        s = Serializer(Config.SECRET_KEY)
        try:
            data = s.loads(token, salt='email-verify-salt', max_age=expires_sec)
            user_id = data['user_id']
            email = data['email']
        except:
            return None
        
        user = User.query.get(user_id)
        if user and user.email == email:
            return user
        return None