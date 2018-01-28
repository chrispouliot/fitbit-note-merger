
import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils.types import ChoiceType

from config import app

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
