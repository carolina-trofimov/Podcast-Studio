from botocore.exceptions import ClientError
from constants import s3, s3_client, bucket
from flask import (Flask, render_template, redirect, request, flash, session, url_for, jsonify)
from flask_debugtoolbar import DebugToolbarExtension
from flask_uploads import UploadSet, configure_uploads, AUDIO
from helpers import allowed_file, delete_from_s3, delete_from_db, save_file_to_s3, save_audio_to_db
import io
from jinja2 import StrictUndefined
import logging
from model import connect_to_db, db, AudioType, User, Audio
from pydub import AudioSegment
from sqlalchemy import update
from werkzeug.utils import secure_filename


app = Flask(__name__)
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
    username = request.form.get("username")
    user = User.query.filter_by(email=email).first()

    if username == username:
        session["logged_in_user"] = user.user_id
        return redirect("/upload")
    else:
        flash("Incorrect email or password.")
        return redirect("/upload")


@app.route("/upload")
def upload():
    """Show upload form."""
    return render_template('upload_mp3.html')


@app.route("/process-upload", methods=["POST"])
def process_upload():
    """Upload file to S3 and add it to database."""
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

    # Download s3 audio object 
    file1 = io.BytesIO()
    s3.Object("podcaststudio", f"raw_podcasts/{pod.name}").download_fileobj(file1)
    #reset seeking
    file1.seek(0) 
    #convert audio into audiosegment object
    audio1 = AudioSegment.from_file(file1, format="mp3")
    
    ad_id = request.form.get("ad_id")
    ad = Audio.query.get(ad_id)

    file2 = io.BytesIO()
    s3.Object("podcaststudio", f"ads/{ad.name}").download_fileobj(file2)
    file2.seek(0)
    audio2 = AudioSegment.from_file(file2, format="mp3")

    # append ad into podcast
    edited_pod = audio2.append(audio1, crossfade=2000)
    
    file3 = io.BytesIO()
    edited_pod.export(file3, format="mp3")
    file3.seek(0)
    
    save_file_to_s3(f"{pod.name}-{ad.name}", "edit", file3)
    save_audio_to_db(f"{pod.name}-{ad.name}", "edit")

    return redirect("/my-podcasts")


@app.route("/my-podcasts")
def my_podcasts():
    """Show list of podcasts edited with ad"""
    user = User.query.get(session["logged_in_user"])
    all_edited_podcasts = Audio.query.filter_by(user_id=user.user_id, audio_code='edit').all()
    return render_template("my_podcasts.html", audios=all_edited_podcasts)


@app.route("/publish", methods=["POST"])
def publish():
    """Allow user to publish their pdocasts"""

    user = User.query.get(session["logged_in_user"])
    audio_id = request.form.get("publish")
    audio = Audio.query.get(audio_id)

    if request.form.get("action") == "publish":      
        print("publishing: ", audio.name)
        audio.published = True
        db.session.add(audio)
        db.session.commit()
        return jsonify({"status": "published"})

    else: 
        audio.published = False
        db.session.add(audio)
        db.session.commit()
        return jsonify({"status": "unpublished"})


@app.route("/users", methods=["POST", "GET"])
def all_users():
    """Show list of users to follow"""

    user = User.query.get(session["logged_in_user"])
    users = user.query.filter(User.uname != user.uname).all()
    return render_template("users.html", users=users, loggedin_user=user)


@app.route("/handle-follow", methods=["POST"])
def handle_follow():
    
    user = User.query.get(session["logged_in_user"])
    followed_id = request.form.get("followed")
    followed = User.query.get(followed_id)

    if request.form.get("action") == "follow":      
        if followed not in user.following:
            user.following.append(followed)
            db.session.commit()
        return jsonify({"status": "following"})

    else: 
        user.following.remove(followed)
        db.session.commit()
        return jsonify({"status": "unfollowing"})


@app.route("/user/<int:user_id>", methods=["GET", "POST"])
def profile(user_id):
    """Show user profile with published podcasts"""                                   
    
    user = User.query.get(session["logged_in_user"])
    to_follow = User.query.get(user_id)
    audio = Audio.query.filter_by(user_id=to_follow.user_id, audio_code="edit", published=True)
    return render_template("profile.html", audios=audio, user=user, to_follow=to_follow) 


@app.route("/delete-audio/<int:audio_id>", methods=["GET", "POST"])
def delete_audio(audio_id):
    """Allow user to delete an audio"""
    user = User.query.get(session["logged_in_user"])
    if user:
        audio = Audio.query.filter_by(audio_id=audio_id).one()
        if audio.audio_code == "ad":    
            delete_from_db(audio, audio.audio_code)
            delete_from_s3("ads", audio.name)
            return redirect("/my-ads")

        elif audio.audio_code == "pod":
            delete_from_db(audio, audio.audio_code)
            delete_from_s3("pod", audio.name)
            return redirect("/my-raw-podcasts")

        elif audio.audio_code == "edit":
            delete_from_db(audio, audio.audio_code)
            delete_from_s3("edit", audio.name)
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