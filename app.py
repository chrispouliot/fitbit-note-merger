import datetime
import os

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
db = SQLAlchemy(app)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.String(250))
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<Note %r %r>' % (self.created_date, self.note)


@app.errorhandler(Exception)
def error(error):
    return render_template('index.html', response="An error occured: {}".format(error))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/note', methods=['POST'])
def create_note():
    note = request.form.get('note')
    if not note:
        return render_template('index.html', response="No note provided")

    note = Note(note=note)
    db.session.add(note)
    db.session.commit()

    return render_template('index.html', response="Note created")


@app.route('/note', methods=['GET'])
def list_notes():
    notes = Note.query.all()
    return render_template('index.html', response="Retrieved notes", notes=notes)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
