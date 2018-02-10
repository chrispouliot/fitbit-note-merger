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


class BodyParameters(object):
    REQUEST_TOKEN_PARAMS = {
        'client_id': fitbit_client_id,
        'response_type': 'code',
        'scope': 'activity nutrition profile sleep weight',
        'expires_in': '2592000',  # 30 days
    }
    COMPLETE_AUTH_PARAMS = {
        'code': None,
        'client_id': fitbit_client_id,
        'grant_type': 'authorization_code',
    }
    REFRESH_AUTH_PARAMS = {
        'refresh_token': None,
        'grant_type': 'refresh_token',
    }


class FitbitError(Exception):
    pass


def get_authorize_url():
    return f'{authorize_url}?{urlencode(BodyParameters.REQUEST_TOKEN_PARAMS, quote_via=quote_plus)}'


def _send_auth(data):
    r = requests.post(
        access_token_url,
        auth=(fitbit_client_id, fitbit_client_secret),
        data=data,
    )

    if r.status_code > 400:
        raise FitbitError("We did a wrong! code:{} '{}'".format(r.status_code, r.text))

    json = r.json()
    user_id = json.get('user_id')
    expires_in = json.get('expires_in')
    now = datetime.datetime.now()
    expiry_date = now + datetime.timedelta(seconds=expires_in)

    return Auth.save(
        user_id=user_id,
        access_token=json.get('access_token'),
        refresh_token=json.get('refresh_token'),
        expiry_date=expiry_date.timestamp(),
    )


def complete_auth(auth_code):
    data = BodyParameters.COMPLETE_AUTH_PARAMS
    data['code'] = auth_code
    auth = _send_auth(data)
    return auth.user_id


def refresh_token(user_id):
    refresh_token = Auth.get_auth(user_id=user_id).refresh_token
    data = BodyParameters.REFRESH_AUTH_PARAMS
    data['refresh_token'] = refresh_token
    _send_auth(data)


def get_food_log(user_id, retry_count=0):
    access_token = Auth.get_auth(user_id).access_token
    # TODO: Support more than just todays food log. Also not just PST
    today = datetime.datetime.now(tz=pytz.utc).astimezone(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d')
    url = food_api_url.format(user_id=user_id, date=today)
    headers = {"Authorization": "Bearer {}".format(access_token)}

    r = requests.get(url, headers=headers)
    if r.status_code >= 400:
        if r.status_code == 401 and retry_count < 1:
            print('Expired access token.. refreshing')
            refresh_token(user_id)
            return get_food_log(user_id, retry_count=1)
        raise FitbitError("We did a wrong! code:{} '{}'".format(r.status_code, r.text))

    return DailyFoodlogSerializer.from_json(r.json())
