import os

from flask import Flask

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
port = int(os.environ.get('PORT', 8000))
fitbit_client_id = os.environ.get('FITBIT_CLIENT_ID')
fitbit_client_secret = os.environ.get('FITBIT_CLIENT_SECRET')

