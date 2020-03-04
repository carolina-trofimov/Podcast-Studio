from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()

 

class AudioType(db.Model):
    """Data model for an audio_code."""

    __tablename__ = "audio_types"

    # Define your columns and/or relationships here
    audio_code = db.Column(db.String(10), nullable=False, primary_key=True,)



    def __repr__(self):
        """Return a human-readable representation of an Audio."""

        return f"<audio_code={self.audio_code}>"


class User(db.Model):
    """Data model for an audio."""

    __tablename__ = "users"

    # Define your columns and/or relationships here
    user_id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True,)
    uname = db.Column(db.String(30), nullable=False, unique=True,)
    email = db.Column(db.String(100), nullable=False, unique=True,)
    # password = db.Column(db.String(64), nullable=True) ADD this column???

    def __repr__(self):
        """Return a human-readable representation of an Audio."""

        return f"<uname={self.uname} email{self.email}>"

class Audio(db.Model):
    """Data model for an audio."""

    __tablename__ = "audios"

    # Define your columns and/or relationships here
    audio_id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True,)

    name = db.Column(db.String(50), nullable=False,)

    s3_path = db.Column(db.String(300), nullable=False,)
    
    s3_key = db.Column(db.String(300), nullable=False,)

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

    follow_id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True,)
    
    follower_id = db.Column(db.Integer,
                     db.ForeignKey('users.user_id'),
                     nullable=False,
                     )

    followed_id = db.Column(db.Integer,
                     db.ForeignKey('users.user_id'),
                     nullable=False,
                     )

    follower = db.relationship("User", foreign_keys=[follower_id], backref="following")
    followed = db.relationship("User", foreign_keys=[followed_id], backref="followed_by")

    # follower = relationship("User", foreign_keys="[User.follower_id]")
    # followed = relationship("User", foreign_keys="[User.followed_id]")

    def __repr__(self):
        """Return a human-readable representation of a channel."""

        return f"<follower_id={self.follower_id} followed_id={self.followed_id}>"


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our database.
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///podcasts"
    app.config["SQLALCHEMY_ECHO"] = False
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
