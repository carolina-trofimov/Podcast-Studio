
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

# @app.route('/')
# def index():
#     return render_template('upload_mp3.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST']) # when i delete GET method and the if statment, I get message "Method not allowed."
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # my_podcast = f'/static/uploaded_mp3/{filename}'
            return render_template('my_podcasts.html', filename=filename)
            
            # return redirect(f'/static/uploaded_mp3/{filename}')

    return render_template('upload_mp3.html')

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