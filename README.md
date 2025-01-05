# flask-audio

This is a hobby project to play your MP3 , flac and wav files in your browser

### Architecture

1. Frontend 

   bootstrap and flask 
2. Backend

   postgres sql database

### How to setup

flask shell

from app import db
db.create_all()

this will create the necessary schemas in the database.

then run the program 

python3 app.py