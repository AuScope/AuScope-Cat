import logging
import sys

import requests
from requests.adapters import HTTPAdapter
from urllib3.exceptions import HTTPError
from urllib3.util import Retry

from auscopecat.auscopecat_types import AuScopeCatError

LOG_LVL = logging.INFO
''' Initialise debug level, set to 'logging.INFO' or 'logging.DEBUG'
'''

# Set up debugging
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(LOG_LVL)

if not LOGGER.hasHandlers():

    # Create logging console handler
    HANDLER = logging.StreamHandler(sys.stdout)

    # Create logging formatter
    FORMATTER = logging.Formatter('%(name)s -- %(levelname)s - %(funcName)s: %(message)s')

    # Add formatter to ch
    HANDLER.setFormatter(FORMATTER)

    # Add handler to LOGGER and set level
    LOGGER.addHandler(HANDLER)

def request(url: str, params: dict = None, method:str = 'GET'):
    """
    Send a request to AuScope API

    :param url: URL
    :param params: dictionary of HTTP request parameters
    :param method:  HTTP request method "POST" or "GET"
    :returns: response or [] upon error
    """
    prov = url
    try:
        with requests.Session() as s:

            # Retry with backoff
            retries = Retry(total=5,
                            backoff_factor=0.5,
                            status_forcelist=[429, 502, 503, 504]
                           )
            s.mount('https://', HTTPAdapter(max_retries=retries))

            # Sending the request
            if method == 'GET':
                response = s.get(url, params=params)
            else:
                response = s.post(url, data=params)

    except (HTTPError, requests.RequestException) as e:
        LOGGER.error(f"{prov} returned error exception: {e}")
        raise AuScopeCatError(
            f"{prov} returned error exception: {e}",
            500
        )
    if response.status_code != 200:
        LOGGER.error(f"{prov} returned error {response.status_code} in response: {response.text}")
    return response
