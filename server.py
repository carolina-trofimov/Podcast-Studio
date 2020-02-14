
from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session, url_for)

from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, AudioType, User, Audio

from flask_uploads import UploadSet, configure_uploads, AUDIO

from werkzeug.utils import secure_filename

import os

UPLOAD_FOLDER = 'static/uploaded_mp3'
ALLOWED_EXTENSIONS = {'mp3'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"


app.jinja_env.undefined = StrictUndefined



# @app.route('/google-login')



@app.route('/')
def index():

    return render_template('homepage.html')



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
        # flash("Login successful.")
        session["logged_in_user"] = user.user_id
        return redirect("/process-upload")   # user-information?user={user.user_id}") Actually needs to redirect to /my-podcast when the route is done
    else:
        flash("Incorrect email or password.")
        return redirect("/login")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/process-upload') 
def upload_file():


 return render_template('upload_mp3.html')


@app.route('/process-upload', methods=['POST'])
def process_upload():
                                                                                #audio = Audio.query.all()

    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        audio_type = AudioType.query.get('pod')
        user = User.query.get(session['logged_in_user'])
        audio = Audio(user=user, audio_type=audio_type, name=filename, s3_path=os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.session.add(audio)                                                 #if user add podcast audio:
        db.session.commit()                                                       #redirect("/my_podcasts")
        flash("Audio added")                                                    #else:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))              #redirect("/my_ads")

        return redirect('/my-podcasts')

                

            
@app.route('/my-podcasts')
def my_podcasts():

    user = User.query.get(session['logged_in_user'])
    


    return render_template('my_podcasts.html', audios=user.audios)

                                    

            
@app.route('/my-ads')
def my_ads():

    return render_template('my_ads.html')



@app.route("/logout")
def logout():
    """Logout user."""

    del session["logged_in_user"]
    flash("Logout successful.")

    return redirect("/")

# @app.route('/raw-podcast')
    
# when I have an successfull upload I don't want it to start playing, i want
# to redirect to user homepage where they can see all the audios uploaded.


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