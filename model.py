from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

 

class AudioType(db.Model):
    """Data model for a human."""

    __tablename__ = "audio_types"

    # Define your columns and/or relationships here
    audio_code = db.Column(db.String(10), nullable=False, primary_key=True,)

    def __repr__(self):
        """Return a human-readable representation of an Audio."""

        return f"<audio_code={self.audio_code}>"


class User(db.Model):
    """Data model for a human."""

    __tablename__ = "users"

    # Define your columns and/or relationships here
    user_id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True,)
    uname = db.Column(db.String(30), nullable=False, unique=True,)
    email = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        """Return a human-readable representation of an Audio."""

        return f"<uname={self.uname} email{self.email}>"

class Audio(db.Model):
    """Data model for a human."""

    __tablename__ = "audios"

    # Define your columns and/or relationships here
    audio_id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True,)

    name = db.Column(db.String(50), nullable=False,)

    s3_path = db.Column(db.String(300), nullable=False,)

    published = db.Column(db.Boolean, default=False, nullable=False)

    audio_code = db.Column(db.String(10),
                         db.ForeignKey('audio_types.audio_code'),
                         nullable=False,)

    user_id = db.Column(db.Integer,
                         db.ForeignKey('users.user_id'),
                         nullable=False,
                         )

    user = db.relationship('User', backref='audios')

    def __repr__(self):
        """Return a human-readable representation of an Audio."""

        return f"<audio_id={self.audio_id} name={self.name} audio_code={self.audio_code}>"




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
