from flask import Flask, request, render_template, send_file, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from io import BytesIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@host/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB

db = SQLAlchemy(app)

ALLOWED_EXTENSIONS = {'mp3', 'flac', 'wav'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Define the model for the songs
class Song(db.Model):
    __tablename__ = 'songs'  # Explicitly define the table name
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    artist = db.Column(db.String(255))
    song_data = db.Column(db.LargeBinary, nullable=False)

# Home route to display uploaded songs and a form to upload new ones
@app.route('/', methods=['GET'])
def index():
    search_term = request.args.get('search', '')  # Get the search query from the URL

    if search_term:
        # If there's a search query, filter songs by title or artist
        songs = Song.query.filter(
            (Song.title.ilike(f'%{search_term}%')) |
            (Song.artist.ilike(f'%{search_term}%'))
        ).all()
    else:
        # Otherwise, return all songs
        songs = Song.query.all()

    return render_template('index.html', songs=songs)

# Route to upload MP3 files
@app.route('/upload', methods=['POST'])
def upload_song():
    file = request.files['file']
    title = request.form['title']
    artist = request.form['artist']

    if file and allowed_file(file.filename):
        # Secure the file name to prevent directory traversal attacks
        filename = secure_filename(file.filename)
        
        song_data = file.read()  # Read the content of the file
        new_song = Song(title=title, artist=artist, song_data=song_data)
        db.session.add(new_song)
        db.session.commit()

    return redirect(url_for('index'))
#Route to delete files 
@app.route('/delete/<int:song_id>', methods=['POST'])
def delete_song(song_id):
    # Find the song by its ID
    song_to_delete = Song.query.get(song_id)
    
    # Check if the song exists
    if song_to_delete:
        # Delete the song from the database
        db.session.delete(song_to_delete)
        db.session.commit()
    
    # Redirect back to the homepage
    return redirect(url_for('index'))
# Route to play an MP3 file
@app.route('/play/<int:song_id>')
def play_song(song_id):
    song = Song.query.get_or_404(song_id)
    return send_file(BytesIO(song.song_data), mimetype="audio/mpeg", as_attachment=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

