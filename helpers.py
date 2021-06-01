from boto.s3.connection import S3Connection, Bucket, Key
from constants import ALLOWED_EXTENSIONS, s3_client, s3, bucket
from flask import flash, redirect, session
from functools import wraps
from model import AudioType, User, Audio, db
import os
from os import environ

aws_secret_access_key = environ.get("AWS_SECRET_ACCESS_KEY")
aws_access_key_id = environ.get("AWS_ACCESS_KEY_ID")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = dict(session).get('logged_in_user', None)
        # You would add a check here and usethe user id or something to fetch
        # the other data for that user/check if they exist
        if user:
            return f(*args, **kwargs)
        else:
            # flash("You are not logged in")
            return redirect("/")
    return decorated_function


def allowed_file(filename):
    """Check if file is in the correct extension mp3."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

     
def save_file_to_s3(filename, audio_type, file):
    """Save file to S3 bucket"""
    if audio_type == "podcast":
        s3_path = f"raw_podcasts/{filename}"
    elif audio_type == "ad":
        s3_path = f"ads/{filename}"
    else:
        s3_path = f"podcasts/{filename}"
    
    s3_client.put_object(Body=file,
                      Bucket="podcaststudio",
                      Key=s3_path,
                      ContentType="mp3",
                      ACL="public-read")


def save_audio_to_db(filename, audio_type, user):
    """Save audio to databade"""

    if audio_type == "podcast":
        s3_path = f"https://podcaststudio.s3-us-west-1.amazonaws.com/raw_podcasts/{filename}"
    elif audio_type == "ad":
        s3_path = f"https://podcaststudio.s3-us-west-1.amazonaws.com/ads/{filename}"
    else:
        s3_path = f"https://podcaststudio.s3-us-west-1.amazonaws.com/podcasts/{filename}"
    audio_type = AudioType.query.get(audio_type)

    audio = Audio(user=user, audio_type=audio_type, name=filename, s3_path=s3_path)
    db.session.add(audio)
    db.session.commit()
    return audio.audio_code


def delete_from_s3(folder, audio_name):
    """Delete audio from S3 bucket"""
    conn = S3Connection(aws_access_key_id, aws_secret_access_key)
    bucket = Bucket(conn, "podcaststudio")
    k = Key(bucket)
    k.key = f"{folder}/{audio_name}"
    bucket.delete_key(k)


def delete_from_db(audio):
    """Delete audio from database"""
    db.session.delete(audio)
    db.session.commit()