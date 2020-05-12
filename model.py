from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship


db = SQLAlchemy()

 
class AudioType(db.Model):
    """Data model for an audio_code."""

    __tablename__ = "audio_types"

    audio_code = db.Column(db.String(10), nullable=False, primary_key=True,)

    def __repr__(self):
        """Return a human-readable representation of an Audio."""
        return f"<audio_code={self.audio_code}>"


class User(db.Model):
    """Data model for an user."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=False)
    tokens = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())

    following = db.relationship(
        'User',
        secondary='followers',
        primaryjoin='User.user_id==Follow.follower_id',
        secondaryjoin='User.user_id==Follow.followed_id',
        backref='followers'
    )

    def __repr__(self):
        """Return a human-readable representation of an User."""
        return f"<username={self.username} email{self.email}>"


class Audio(db.Model):
    """Data model for an audio."""

    __tablename__ = "audios"

    audio_id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True,)
    name = db.Column(db.String(50), nullable=False,)
    s3_path = db.Column(db.String(300), nullable=False,)
    published = db.Column(db.Boolean, default=False, nullable=False,)
    audio_code = db.Column(db.String(10),
                         db.ForeignKey('audio_types.audio_code'),
                         nullable=False,)
    user_id = db.Column(db.Integer,
                         db.ForeignKey('users.user_id'),
                         nullable=False,
                         )
    user = db.relationship('User', backref='audios')
    audio_type = db.relationship('AudioType', backref='audios')  

    def __repr__(self):
        """Return a human-readable representation of an Audio."""
        return f"<audio_id={self.audio_id} name={self.name} audio_code={self.audio_code}>"


class Follow(db.Model):
    """Data model for a channel"""

    __tablename__ = "followers"
    __table_args__ = (
        db.UniqueConstraint('follower_id', 'followed_id'),
    )
    follow_id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True,)
    follower_id = db.Column(db.Integer,
                     db.ForeignKey('users.user_id'),
                     nullable=False,
                     )
    followed_id = db.Column(db.Integer,
                     db.ForeignKey('users.user_id'),
                     nullable=False,
                     )

    def __repr__(self):
        """Return a human-readable representation of followers."""
        return f"<follower_id={self.follower_id} followed_id={self.followed_id}>"


def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///podcasts"
    app.config["SQLALCHEMY_ECHO"] = False
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


def seed_db(): 
    """seed database"""
    db.session.add(AudioType(audio_code="podcast"))
    db.session.add(AudioType(audio_code="ad"))
    db.session.add(AudioType(audio_code="edit"))
    db.session.commit()
    

if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    db.create_all()
    seed_db()
