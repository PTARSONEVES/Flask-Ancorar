from ..database import db
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(length=200), nullable=False, unique=True)
    email = db.Column(db.String(length=200), nullable=False, unique=True)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    emal_confirmed = db.Column(db.String(length=1),nullable=True, default='0')
    password = db.Column(db.String(length=30), nullable=False, unique=True)
    remember_token = db.Column(db.Text nullable=True)
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
