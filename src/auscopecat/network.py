import sys
import logging
from urllib3.util import Retry
import requests
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.exceptions import HTTPError

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
    :returns: response 
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
        return []
    if response.status_code != 200:
        LOGGER.error(f"{prov} returned error {response.status_code} in response: {response.text}")
    return response


def requestWFS(url: str, params: dict = None, method:str = 'GET'):
    """
    Send a WFS request

    :param url: URL 
    :param params: dictionary of HTTP request parameters
    :param method:  HTTP request method "POST" or "GET"
    :returns: response 
    """
    prov = url
    if params == None:
        params = {
                "service": "WFS",
                "version": "1.1.0",
                "request": "GetFeature",
                "typename": "gsmlp:BoreholeView",
                "outputFormat": "json",
                "FILTER": "<ogc:Filter><ogc:PropertyIsEqualTo matchCase=\"false\"><ogc:PropertyName>gsmlp:nvclCollection</ogc:PropertyName><ogc:Literal>true</ogc:Literal></ogc:PropertyIsEqualTo></ogc:Filter>",
                "maxFeatures": str(10)
                } 

    res = request(url, params, method)
    return res

def requestWMS(url: str, params: dict = None, method:str = 'GET'):
    """
    Send a WMS request

    :param url: URL 
    :param params: dictionary of HTTP request parameters
    :param method:  HTTP request method "POST" or "GET"
    :returns: response 
    """
    prov = url
    if params == None:
        params = {
                "service": "WMS",
                "version": "1.1.1",
                "request": "GetMap",
                "layers": "gsmlp:BoreholeView",
                "format": "image/png",
                "style": "",
                "BGCOLOR": "0xFFFFFF",
                "TRANSPARENT": "TRUE",
                "SRS": "EPSG:4326",
                "BBOX": "105.53333332790065,-35.033522303030146,129.01666666127286,-10.415345166691509",
                "WIDTH": "400",
                "HEIGHT": "400"
                }    

    res = request(url, params, method)
    return res
