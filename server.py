
from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request, flash, session, url_for)
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, AudioType, User, Audio
from flask_uploads import UploadSet, configure_uploads, AUDIO
from werkzeug.utils import secure_filename
import os
from pydub import AudioSegment
# from ffprobe import FFProbe

UPLOAD_FOLDER = "static/uploaded_mp3"
ALLOWED_EXTENSIONS = {"mp3"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

app.jinja_env.undefined = StrictUndefined

# @app.route('/google-login')


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

    if User.query.filter_by(email=new_email).first() is None:
        user = User(email=new_email, uname=new_email) #, password=new_password)
        db.session.add(user)
        db.session.commit()
        flash("New user created.") 
        return redirect("/")
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
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if password == password:
        session["logged_in_user"] = user.user_id
        return redirect("/upload")
    else:
        flash("Incorrect email or password.")
        return redirect("/login")


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
        audio_type = AudioType.query.get(audio_type)
        user = User.query.get(session["logged_in_user"])
        audio = Audio(user=user, audio_type=audio_type, name=filename, s3_path=os.path.join(app.config["UPLOAD_FOLDER"], filename))
        db.session.add(audio)
        db.session.commit()
        flash("Audio added")
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        if audio.audio_code == "pod":

            return redirect("/my-raw-podcasts")
        else:

            return redirect("/my-ads")
                

@app.route("/my-raw-podcasts")
def my_podcasts():
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

@app.route("/concatenate-audios")
def concatenate_audios():
    """Allow user to add an ad into a podcast audio"""
    # #example    
    # # audio1 = AudioSegment.from_file("/path/to/audio1.mp3", format="mp3")
    # # audio2 = AudioSegment.from_file("/path/to/audio2.mp3", format="mp3")
    # # podcast = audio1.append(sound2, crossfade=2000)

    user = User.query.get(session["logged_in_user"])

    # print("this is a list >>>>>>>>>>>>>>>>>>>>>>>", user.audios)
    # audio_object = user.audios # this is a list of audio objects

    #instantiate audio object as pod to access podcast name to concatenate
    pod = user.audios[0]
    # print("this is a path >>>>>>>>>>>>>>>", pod.s3_path)
    audio1 = AudioSegment.from_file(pod.s3_path, format="mp3")
    #instantiate audio object as ad to access ad name to concatenate
    # print("this is audio1 >>>>>>>>>>>>>", audio1)
    ad = user.audios[1]
    audio2 = AudioSegment.from_file(ad.s3_path, format="mp3")

    # edited_pod = audio2 + audio1
    edited_pod = audio1.append(audio2, crossfade=2000).export("static/podcasts/edited_pod.mp3", format="mp3")
    # edited_pod.export("/static/podcasts", format="mp3")


    db.session.add(edited_pod)
    db.session.commit()

    return render_template("my_podcasts.html", edited_pod=edited_pod)



# @app.route("/delete-audio/<int:<audio_id/", methods=["GET", "POST"])
# def delete_audio(audio_id):
#     """Allow user to delete an audio"""
#     new_id

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