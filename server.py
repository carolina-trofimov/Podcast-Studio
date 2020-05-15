from authlib.integrations.flask_client import OAuth, token_update
from botocore.exceptions import ClientError
from constants import s3, s3_client, bucket
from flask import (Flask, render_template, redirect, request, flash, session, url_for, jsonify)
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager, logout_user
from flask_uploads import UploadSet, configure_uploads, AUDIO
from helpers import allowed_file, delete_from_s3, delete_from_db, login_required, save_file_to_s3, save_audio_to_db
import io
from jinja2 import StrictUndefined
import logging
from model import connect_to_db, db, AudioType, User, Audio
import os
from os import environ
from pydub import AudioSegment
import requests
from sqlalchemy import update
from werkzeug.utils import secure_filename




app = Flask(__name__)
app.secret_key = environ.get("app_secret_key")
app.jinja_env.undefined = StrictUndefined

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth = OAuth(app)
oauth.register(
    name='google',
    client_id=os.environ.get("google_oauth_client_id"),
    client_secret=os.environ.get("google_oauth_client_secret"),
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)


@token_update.connect_via(app)
def on_token_update(sender, name, token, refresh_token=None, access_token=None):

    if refresh_token:
        item = OAuth2Token.find(name=name, refresh_token=refresh_token)
    elif access_token:
        item = OAuth2Token.find(name=name, access_token=access_token)
    else:
        return

    # update old token
    item.access_token = token['access_token']
    item.refresh_token = token.get('refresh_token')
    item.expires_at = token['expires_at']
    item.save()

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/google-login")
def google_login():
    user = dict(session).get("logged_in_user", None)
    if not user:
        return redirect("/login")
    else:
        return redirect("/upload")


@app.route('/login')
def login():
    google = oauth.create_client("google")
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    token = oauth.google.authorize_access_token()
    user = oauth.google.parse_id_token(token)
    session['logged_in_user'] = user
    user_model = User.query.filter_by(email=(user['email'])).first()

    if not user_model:
        new_user = User(email=user["email"], username=user["name"], avatar=user["picture"], tokens=token["access_token"])
        print(f"new_user: {new_user}")
        db.session.add(new_user)
        db.session.commit()
    else:
        user_model.tokens = token["access_token"]
        db.session.commit()



    return redirect('/upload')    

@app.route("/upload")
@login_required
def upload():
    """Show upload form."""
    return render_template('upload_mp3.html')


@app.route("/process-upload", methods=["POST"])
def process_upload():
    """Upload file to S3 and add it to database."""

    user = User.query.filter_by(email=session["logged_in_user"]["email"]).first()

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
        save_audio_to_db(filename, audio_type, user)

        flash("Audio added")

        if audio_type == "podcast":
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
@login_required
def my_raw_podcasts():
    """Show raw-podcast list."""
   
    user = User.query.filter_by(email=session["logged_in_user"]["email"]).first()
    audio = Audio.query.filter_by(user_id=user.user_id, audio_code="podcast")

    return render_template("my_raw_podcasts.html", audios=audio)

          
@app.route("/my-ads")
@login_required
def my_ads():
    """Show ads list."""
    user = User.query.filter_by(email=session["logged_in_user"]["email"]).first()
    audio = Audio.query.filter_by(user_id=user.user_id, audio_code="ad")
    return render_template("my_ads.html", audios=audio)


@app.route("/choose-ad")
def choose_ad():
    """Allow user to choose and ad"""
    user = User.query.filter_by(email=session["logged_in_user"]["email"]).first()
    audios = user.audios
    return render_template("choose_ad.html", audios=audios)


@app.route("/concatenate-audios", methods=["GET", "POST"])
def concatenate_audios():
    """Allow user to add an ad into a podcast audio"""

    user = User.query.filter_by(email=session["logged_in_user"]["email"]).first()
    #instantiate audio object as podcast to access podcast name to concatenate
    podcast_id = request.form.get("raw_podcast_id")
    podcast = Audio.query.get(podcast_id)

    # Download s3 audio object 
    file1 = io.BytesIO()
    s3.Object("podcaststudio", f"raw_podcasts/{podcast.name}").download_fileobj(file1)
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
    edited_podcast = audio2.append(audio1, crossfade=2000)
    
    file3 = io.BytesIO()
    edited_podcast.export(file3, format="mp3")
    file3.seek(0)
    
    save_file_to_s3(f"{podcast.name}-{ad.name}", "edit", file3)
    save_audio_to_db(f"{podcast.name}-{ad.name}", "edit", user)

    return redirect("/my-podcasts")


@app.route("/my-podcasts")
@login_required
def my_podcasts():
    """Show list of podcasts edited with ad"""
    user =User.query.filter_by(email=session["logged_in_user"]["email"]).first()
    all_edited_podcasts = Audio.query.filter_by(user_id=user.user_id, audio_code='edit').all()
    return render_template("my_podcasts.html", audios=all_edited_podcasts)


@app.route("/publish", methods=["POST"])
def publish():
    """Allow user to publish their pdocasts"""

    user = User.query.filter_by(email=session["logged_in_user"]["email"]).first()
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

    user = dict(session).get("logged_in_user", None)
    if user:
        user = User.query.filter_by(email=session["logged_in_user"]["email"]).first()
        users = user.query.filter(User.email != user.email).all()

    else:
        users = User.query.all()
    
    return render_template("users.html", users=users, loggedin_user=user)


@app.route("/handle-follow", methods=["POST"])
@login_required
def handle_follow():
    
    user = User.query.filter_by(email=session["logged_in_user"]["email"]).first()
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
    user = dict(session).get("logged_in_user", None)
    
    if user:
        user = User.query.filter_by(email=session["logged_in_user"]["email"]).first()
        to_follow = User.query.get(user_id)
        audio = Audio.query.filter_by(user_id=to_follow.user_id, audio_code="edit", published=True)
    else:
        to_follow = User.query.get(user_id)
        audio = Audio.query.filter_by(user_id=to_follow.user_id, audio_code="edit", published=True)

    return render_template("profile.html", audios=audio, user=user, to_follow=to_follow) 


@app.route("/delete-audio/<int:audio_id>", methods=["GET", "POST"])
@login_required
def delete_audio(audio_id):
    """Allow user to delete an audio"""
    user = User.query.filter_by(email=session["logged_in_user"]["email"]).first() 
    if user:
        audio = Audio.query.filter_by(audio_id=audio_id).one()
        if audio.audio_code == "ad":    
            delete_from_db(audio)
            delete_from_s3("ads", audio.name)
            return redirect("/my-ads")

        elif audio.audio_code == "podcast":
            delete_from_db(audio)
            delete_from_s3("podcast", audio.name)
            return redirect("/my-raw-podcasts")

        elif audio.audio_code == "edit":
            delete_from_db(audio)
            delete_from_s3("edit", audio.name)
            return redirect("/my-podcasts")


@app.route("/logout")
def logout():
    """Logout user."""

    user = User.query.filter_by(email=session["logged_in_user"]["email"]).first() 

    if user:
        del session["logged_in_user"] 

    response = requests.get(f"https://accounts.google.com/o/oauth2/revoke?token={user.tokens}")

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