from flask import render_template, redirect, request, session

from db import db, Note
from config import app, port
from fitbit import get_authorize_url


@app.errorhandler(Exception)
def error(error):
    return render_template('index.html', response="An error occured: {}".format(error))


@app.route('/')
def index():
    # make middleware redirect to /login and do this there?
    return redirect(get_authorize_url(), code=302)
    # returnrender_template('index.html')


@app.route('/auth_callback/<code>', methods=['GET'])
def auth_callback(code):
    print(code)
    return render_template('index.html')


@app.route('/note', methods=['POST'])
def create_note():
    text = request.form.get('note')
    classifier = request.form.get('classifier')
    if not text:
        return render_template('index.html', response="No text provided")
    # TODO: Model doesnt seem to validate?
    if classifier and classifier not in [choices[0] for choices in Note.classifier_choices]:
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
    app.run(host='0.0.0.0', port=port, debug=True)
