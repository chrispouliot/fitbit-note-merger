
import datetime

from flask import session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils.types import ChoiceType
from sqlalchemy.orm.exc import NoResultFound

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
        return '<Note created[%r] text[%r]>' % (self.created_date, self.text)

    @staticmethod
    def save(text, classifier):
        note = Note(text=text, classifier=classifier)
        db.session.add(note)
        db.session.commit()
        return note

    @staticmethod
    def list_notes(days=1):
        return Note.query.filter(Note.created_date > datetime.datetime.now() - datetime.timedelta(days=days))


class Auth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(250))
    expiry_date = db.Column(db.DateTime)
    access_token = db.Column(db.String(250))
    refresh_token = db.Column(db.String(250))

    def __repr__(self):
        return '<Auth usr[%r] expiry[%r]>' % (self.user_id, self.expiry_date)

    @staticmethod
    def save(user_id, access_token, refresh_token, expiry_date):
        auth = Auth.get_auth(user_id)
        if not auth:
            auth = Auth()
        auth.user_id = user_id
        auth.access_token = access_token
        auth.refresh_token = refresh_token
        auth.expiry_date = datetime.datetime.fromtimestamp(int(expiry_date))

        db.session.add(auth)
        db.session.commit()
        return auth

    @staticmethod
    def get_auth(user_id):
        try:
            auth = Auth.query.filter(Auth.user_id == user_id).one()
        except NoResultFound:
            auth = None
        return auth

    @staticmethod
    def is_auth_expired():
        expiry_timestamp = session.get('expiry')
        return datetime.datetime.fromtimestamp(int(expiry_timestamp)) < datetime.datetime.now()
