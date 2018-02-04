from flask import render_template, redirect, request, session

from db import Note
from config import app, port
from fitbit import complete_auth, get_authorize_url, get_food_log


# @app.errorhandler(Exception)
def error(error):
    print(error)
    return render_template('index.html', response="An error occured: {}".format(error))


@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(get_authorize_url())
    return render_template('index.html')


@app.route('/auth_callback')
def auth_callback():
    session['user_id'] = complete_auth(request.args.get('code'))
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

    Note.create_note(text, classifier)
    return render_template('index.html', response="Note created")


@app.route('/note')
def list_notes():
    return render_template('index.html', response="Retrieved notes", notes=Note.list_notes())


@app.route('/food')
def list_food():
    food_log = get_food_log(session.get('user_id'))
    return render_template('index.html', response="Retrieved food log", food=food_log)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)
