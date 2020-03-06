import boto3
import boto
from boto.s3.connection import S3Connection, Bucket, Key
import logging
from botocore.exceptions import ClientError
from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request, flash, session, url_for)
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, AudioType, User, Audio
from flask_uploads import UploadSet, configure_uploads, AUDIO
from werkzeug.utils import secure_filename
import os
import io
from pydub import AudioSegment
from aws_keys import aws_access_key_id, aws_secret_access_key

# use Amazon S3
s3 = boto3.resource('s3')
s3_client = s3.meta.client
bucket = s3.Bucket('podcaststudio')


ALLOWED_EXTENSIONS = {"mp3"}

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

app.jinja_env.undefined = StrictUndefined


@app.route("/")
def index():
    """Show the homepage."""
    return render_template("homepage.html")


@app.route("/register")
def register():
    """Show registration form."""
    return render_template("register.html")


@app.route("/handle-registration", methods=["POST"])
def register_user():
    """Register a new user."""
    new_email = request.form.get("email")
    new_password = request.form.get("password")
    uname = request.form.get("uname")

    if User.query.filter_by(email=new_email).first() is None:
        user = User(uname=uname, email=new_email)
        db.session.add(user)
        db.session.commit()
        flash("New user created.") 
        return redirect("/upload")
    else:
        flash("This user already exists.")
        return redirect("/login")

@app.route("/login")
def show_login_form():
    """Show login form."""
    return render_template("login.html")


@app.route("/handle-login", methods=["POST"])
def login():
    """Login user."""
    email = request.form.get("email")
    # password = request.form.get("password")
    username = request.form.get("username")

    user = User.query.filter_by(email=email).first()

    if username == username:
        session["logged_in_user"] = user.user_id
        return redirect("/upload")
    else:
        flash("Incorrect email or password.")
        return redirect("/upload")


def allowed_file(filename):
    """Check if file is in the correct extension mp3."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload")
def upload():
    """Show upload form."""
    return render_template('upload_mp3.html')


@app.route("/process-upload", methods=["POST"])
def process_upload():
    """Save uploaded file and add it to database."""
    if 'file' not in request.files:
        flash("No file found")
        return redirect('/upload')

    file = request.files["file"]
    if file.filename == "":
        flash("No selected file")
        return redirect("/upload")

    if file and allowed_file(file.filename):

        filename = secure_filename(file.filename) 
        audio_type = request.form.get("audio_type")

        save_file_to_s3(filename, audio_type, request.files['file'])
        save_audio_to_db(filename, audio_type)

        flash("Audio added")

        if audio_type == "pod":
            return redirect("/my-raw-podcasts")
        else:
            return redirect("/my-ads")
   
   #refactor functions below into helper     
def save_file_to_s3(filename, audio_type, file):

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


@app.route("/audio/<int:audio_id>", methods=["POST"])
def edit_audio_name(audio_id):
    
    new_name = request.form.get("name")
    audio = db.session.query(Audio).get(audio_id)
    audio.name = new_name
    db.session.commit()

    return "200"

@app.route("/my-raw-podcasts")
def my_raw_podcasts():
    """Show raw-podcast list."""
    user = User.query.get(session["logged_in_user"])
    audio = Audio.query.filter_by(user_id=user.user_id, audio_code="pod")
    return render_template("my_raw_podcasts.html", audios=audio)


            
@app.route("/my-ads")
def my_ads():
    """Show ads list."""
    user = User.query.get(session["logged_in_user"])
    audio = Audio.query.filter_by(user_id=user.user_id, audio_code="ad")
    return render_template("my_ads.html", audios=audio)


@app.route("/choose-ad")
def choose_ad():
    """Allow user to choose and ad"""
    user = User.query.get(session["logged_in_user"]) #user_id
    
    audios = user.audios

    
    return render_template("choose_ad.html", audios=audios)

@app.route("/concatenate-audios", methods=["GET", "POST"])
def concatenate_audios():
    """Allow user to add an ad into a podcast audio"""

    user = User.query.get(session["logged_in_user"])
    #instantiate audio object as pod to access podcast name to concatenate
    pod_id = request.form.get("raw_pod_id")
    pod = Audio.query.get(pod_id)
    # print("\n\n\n\n\n\n\n\n\n\n", pod.name)
    file1 = io.BytesIO()
    s3.Object("podcaststudio", f"raw_podcasts/{pod.name}").download_fileobj(file1)
    file1.seek(0) 
    audio1 = AudioSegment.from_file(file1, format="mp3")
    #instantiate audio object as ad to access ad name to concatenate
    # print("\n\n\n\n\nthis is audio1 >>>>>>>>>>>>>", audio1, "\n\n\n\n\n\n\n")
    ad_id = request.form.get("ad_id")
    ad = Audio.query.get(ad_id)

    # print("\n\n\n\n\n\n\n\n", ad.s3_path)
    file2 = io.BytesIO()
    s3.Object("podcaststudio", f"ads/{ad.name}").download_fileobj(file2)
    file2.seek(0)
    audio2 = AudioSegment.from_file(file2, format="mp3")

    # edited_pod = audio2 + audio1
    edited_pod = audio2.append(audio1, crossfade=2000)
    
    file3 = io.BytesIO()
    edited_pod.export(file3, format="mp3")
    file3.seek(0)
    
    save_file_to_s3(f"{pod.name}-{ad.name}", "edit", file3)
    save_audio_to_db(f"{pod.name}-{ad.name}", "edit")

    # podcast_result = Audio(name=f"{pod.name}-{ad.name}", s3_path=f"https://podcaststudio.s3-us-west-1.amazonaws.com/podcasts/{pod.name}-{ad.name}", audio_code='edit', user=user)

    # db.session.add(podcast_result)
    # db.session.commit()

    
    return redirect("/my-podcasts")

@app.route("/my-podcasts")
def my_podcasts():
    user = User.query.get(session["logged_in_user"])
    edit_pod = Audio.query.filter_by(user_id=user.user_id, audio_code='edit')

    return render_template("my_podcasts.html", audios=edit_pod)


@app.route("/publish/<int:audio_id>", methods=["POST", "GET"])
def publish(audio_id):

    podcast = Audio.query.get(audio_id)

    not_published = podcast.published

    published = bool(request.form.get("publish"))

    if published:
        audio = db.session.query(Audio).get(audio_id)
        audio.published = published
        db.session.commit()


    return "success"


@app.route("/users", methods=["POST", "GET"])
def all_users():
    """Show list of users"""

    user = User.query.get(session["logged_in_user"])

    users = user.query.filter(User.uname != user.uname).all()

    return render_template("users.html", users=users, logedin_user=user)


@app.route("/handle-follow", methods=["POST"])
def handle_follow():
    
    user = User.query.get(session["logged_in_user"])

    followed_id = request.form.get("followed")


    followed = User.query.get(followed_id)

    user.following.append(followed)

    db.session.commit()
    

    return redirect("/users")


@app.route("/user/<int:user_id>", methods=["GET", "POST"])
def profile(user_id):
    """Shows user profile with edited podcasts"""                                   
    
    user = User.query.get(session["logged_in_user"])

    to_follow = User.query.get(user_id)

    audio = Audio.query.filter_by(user_id=to_follow.user_id, audio_code="edit")

    return render_template("profile.html", audios=audio, user=user, to_follow=to_follow) 



@app.route("/delete-audio/<int:audio_id>", methods=["GET", "POST"])
def delete_audio(audio_id):
    """Allow user to delete an audio"""
    
    user = User.query.get(session["logged_in_user"])
    if user:
        audio = Audio.query.filter_by(audio_id=audio_id).one()

        if audio.audio_code == "ad":    
            # file_to_remove = f"https://podcaststudio.s3-us-west-1.amazonaws.com/ads/{audio.name}"
            
            db.session.delete(audio)
            db.session.commit()

            #def a delete_from_s3 function
            conn = S3Connection(aws_access_key_id, aws_secret_access_key)
            bucket = Bucket(conn, "podcaststudio")
            k = Key(bucket)
            k.key = f"ads/{audio.name}"
            bucket.delete_key(k)

            
            return redirect("/my-ads")


        elif audio.audio_code == "pod":
            # file_to_remove = f"https://podcaststudio.s3-us-west-1.amazonaws.com/raw_podcasts/{audio.name}"
            s3_client.delete_object(Bucket="podcaststudio", Key=audio.s3_path)
            db.session.delete(audio)
            db.session.commit()

            conn = S3Connection(aws_access_key_id, aws_secret_access_key)
            bucket = Bucket(conn, "podcaststudio")
            k = Key(bucket)
            k.key = f"raw_podcasts/{audio.name}"
            bucket.delete_key(k)
            return redirect("/my-raw-podcasts")

        elif audio.audio_code == "edit":
            UPLOAD_FOLDER = "static/podcasts/"

            db.session.delete(audio)
            db.session.commit()

            conn = S3Connection(aws_access_key_id, aws_secret_access_key)
            bucket = Bucket(conn, "podcaststudio")
            k = Key(bucket)
            k.key = f"podcasts/{audio.name}"
            bucket.delete_key(k)

            return redirect("/my-podcasts")


@app.route("/logout")
def logout():
    """Logout user."""

    del session["logged_in_user"] 
    flash("Logout successful.")

    return redirect("/")



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(port=5000, host="0.0.0.0")