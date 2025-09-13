from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()
class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key =True)
    username = db.Column(db.String(200),unique = True)
    email = db.Column(db.String(200),unique =True)
    fullName = db.Column(db.String(200))
    password = db.Column(db.String(200))

class Files(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    filename = db.Column(db.String(200))
    url = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))