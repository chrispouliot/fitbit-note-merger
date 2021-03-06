from flask import render_template, redirect, request, session

from db import Note
from config import app, port
from fitbit import complete_auth, get_authorize_url, get_food_log
from serializers import NoteSerializer


@app.errorhandler(Exception)
def error(error):
    print(error)
    return render_template('index.html', response="An error occured: {}".format(error))


@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(get_authorize_url())
    food_log = get_food_log(session.get('user_id'))
    notes = Note.list_notes(days=3)
    serialized_notes = [NoteSerializer(note) for note in notes]
    return render_template('index.html', food=food_log, notes=serialized_notes)


@app.route('/auth_callback')
def auth_callback():
    session['user_id'] = complete_auth(request.args.get('code'))
    return redirect('/')


@app.route('/note', methods=['POST'])
def create_note():
    text = request.form.get('note')
    classifier = request.form.get('classifier')
    if not text:
        return render_template('index.html', response="No text provided")
    # TODO: Model doesnt seem to validate?
    if classifier and classifier not in [choices[0] for choices in Note.classifier_choices]:
            return render_template('index.html', response="Invalid classifier")

    Note.save(text, classifier)
    return redirect('/')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=False)
