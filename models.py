from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.dialects.postgresql import JSON, ARRAY

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """site user"""
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True,)

    user1_playlist= db.Column(JSON, nullable=True)
    user2_playlist= db.Column(JSON, nullable=True)

    user1_songlist= db.Column(JSON, nullable=True)
    user2_songlist= db.Column(JSON, nullable=True)

    commonSongData = db.Column(JSON, nullable=True)
    # username = db.Column(db.String(20), nullable=False, unique=True)
    # password = db.Column(db.Text, nullable=False)
    # email = db.Column(db.String(50), unique=True, nullable=False)

    @classmethod
    def signup(cls):
        """Sign up user.

        Hashes password and adds user to system.
            """
        
        user = User()

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, id):
        """Find user with `username` and `password`.

            This is a class method (call it on the class, not an individual user.)
            It searches for a user whose password hash matches this password
            and, if it finds such a user, returns that user object.

            If can't find matching user (or if password is wrong), returns False.
            """

        user = cls.query.filter_by(id=id).first()

        if user:    
          return user

        return False