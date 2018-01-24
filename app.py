import datetime
import os

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils.types import ChoiceType

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
db = SQLAlchemy(app)


class Note(db.Model):
    classifier_choices = [
        ('light', 'Light'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('important', 'Important'),
    ]

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(250))
    classifier = db.Column(ChoiceType(classifier_choices))
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<Note %r %r>' % (self.created_date, self.text)


@app.errorhandler(Exception)
def error(error):
    return render_template('index.html', response="An error occured: {}".format(error))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/note', methods=['POST'])
def create_note():
    text = request.form.get('note')
    classifier = request.form.get('classifier')
    if not text:
        return render_template('index.html', response="No text provided")
    # TODO: Model doesnt seem to validate?
    if classifier and classifier not in Note.classifier_choices:
            return render_template('index.html', response="Invalid classifier")

    note = Note(text=text, classifier=classifier)
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
