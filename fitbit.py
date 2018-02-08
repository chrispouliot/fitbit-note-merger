import datetime
import requests
import pytz

from urllib.parse import urlencode, quote_plus

from config import fitbit_client_id, fitbit_client_secret
from db import Auth
from serializers import DailyFoodlogSerializer

food_api_url = 'https://api.fitbit.com/1/user/{user_id}/foods/log/date/{date}.json'
access_token_url = 'https://api.fitbit.com/oauth2/token'
authorize_url = 'https://www.fitbit.com/oauth2/authorize'
request_token_params = {
    'client_id': fitbit_client_id,
    'response_type': 'code',
    'scope': 'activity nutrition profile sleep weight',
    'expires_in': '2592000',  # 30 days
}


class FitbitError(Exception):
    pass


def get_authorize_url():
    return f'{authorize_url}?{urlencode(request_token_params, quote_via=quote_plus)}'


def complete_auth(auth_code):
    r = requests.post(
        access_token_url,
        auth=(fitbit_client_id, fitbit_client_secret),
        data={
            'code': auth_code,
            'client_id': fitbit_client_id,
            'grant_type': 'authorization_code',
        }
    )

    if r.status_code > 400:
        raise FitbitError("We did a wrong! code:{} '{}'".format(r.status_code, r.text))

    json = r.json()
    user_id = json.get('user_id')
    expires_in = json.get('expires_in')
    now = datetime.datetime.now()
    expiry_date = now + datetime.timedelta(seconds=expires_in)

    Auth.save(
        user_id=user_id,
        access_token=json.get('access_token'),
        refresh_token=json.get('refresh_token'),
        expiry_date=expiry_date.timestamp(),
    )

    return user_id


def refresh_token(user_id):
    # TODO: Check if auth exists
    refresh_token = Auth.get_auth(user_id=user_id).refresh_token
    print("Sending refresh token {}".format(refresh_token))
    r = requests.post(
        access_token_url,
        auth=(fitbit_client_id, fitbit_client_secret),
        data={
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }
    )
    if r.status_code >= 400:
        raise FitbitError("We did a wrong! code:{} '{}'".format(r.status_code, r.text))
    print(r.json())
    # TODO: This code is all duplicated
    json = r.json()
    expires_in = json.get('expires_in')
    now = datetime.datetime.now()
    expiry_date = now + datetime.timedelta(seconds=expires_in)

    Auth.save(
        user_id=user_id,
        access_token=json.get('access_token'),
        refresh_token=json.get('refresh_token'),
        expiry_date=expiry_date.timestamp(),
    )


def get_food_log(user_id, retry_count=0):
    access_token = Auth.get_auth(user_id).access_token
    # TODO: Support more than just todays food log. Also not just PST
    today = datetime.datetime.now(tz=pytz.utc).astimezone(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d')
    url = food_api_url.format(user_id=user_id, date=today)
    headers = {"Authorization": "Bearer {}".format(access_token)}

    r = requests.get(url, headers=headers)
    if r.status_code >= 400:
        if r.status_code == 401 and retry_count < 2:
            print('Expired access token.. refreshing')
            refresh_token(user_id)
            return get_food_log(user_id, retry_count=1)
        raise FitbitError("We did a wrong! code:{} '{}'".format(r.status_code, r.text))

    return DailyFoodlogSerializer.from_json(r.json())
