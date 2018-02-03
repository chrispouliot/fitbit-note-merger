from urllib.parse import urlencode, quote_plus

from config import fitbit_client_id

access_token_url = 'https://api.fitbit.com/oauth2/token'
authorize_url = 'https://www.fitbit.com/oauth2/authorize'
request_token_params = {
    'client_id': fitbit_client_id,
    'response_type': 'code',
    'scope': 'activity nutrition profile sleep weight',
    'expires_in': '2592000',  # 30 days
}


class AuthError(Exception):
    pass


def get_authorize_url():
    return f'{authorize_url}?{urlencode(request_token_params, quote_via=quote_plus)}'
