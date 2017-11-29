import requests
from lib import config


def request_html(url, params=None):
    params = params or {}
    res = requests.get(url, headers={'User-Agent': config.USER_AGENT}, params=params)
    if res.status_code != 200:
        raise Exception('Non-200 status code')
    body = res.content
    return body
