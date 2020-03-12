from boto.s3.connection import S3Connection, Bucket, Key
from constants import ALLOWED_EXTENSIONS, s3_client, s3, bucket
from flask import session
from model import AudioType, User, Audio, db
from os import environ

aws_secret_access_key = environ.get("aws_secret_access_key")
aws_access_key_id = environ.get("export aws_access_key_id")


def allowed_file(filename):
    """Check if file is in the correct extension mp3."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

     
def save_file_to_s3(filename, audio_type, file):
    """Save file to S3 bucket"""
    if audio_type == "pod":
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


def save_audio_to_db(filename, audio_type):
    """Save audio to databade"""

    if audio_type == "pod":
        s3_path = f"https://podcaststudio.s3-us-west-1.amazonaws.com/raw_podcasts/{filename}"
    elif audio_type == "ad":
        s3_path = f"https://podcaststudio.s3-us-west-1.amazonaws.com/ads/{filename}"
    else:
        s3_path = f"https://podcaststudio.s3-us-west-1.amazonaws.com/podcasts/{filename}"
    audio_type = AudioType.query.get(audio_type)
    user = User.query.get(session["logged_in_user"])
    print("audio type before query", audio_type)
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


def delete_from_db(audio, audio_code):
    """Delete audio from database"""
    db.session.delete(audio)
    db.session.commit()