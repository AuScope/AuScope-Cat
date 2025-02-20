from io import StringIO
import logging
import sys

import requests

from auscopecat.auscopecat_types import AuScopeCatException
from auscopecat.network import request
import pandas as pd

NVCL_URLS = {
    'VIC': 'https://geology.data.vic.gov.au/nvcl/wfs',
    'NSW': 'https://gs.geoscience.nsw.gov.au/geoserver/wfs',
    'WA': 'https://geossdi.dmp.wa.gov.au/services/wfs',
    'SA': 'https://sarigdata.pir.sa.gov.au/geoserver/wfs',
    'NT': 'https://geology.data.nt.gov.au/geoserver/wfs',
    'QLD': 'https://geology.information.qld.gov.au/geoserver/wfs',
    'CSIRO': 'https://nvclwebservices.csiro.au/geoserver/wfs',
    'TAS': 'https://www.mrt.tas.gov.au/web-services/wfs'
}
MAX_FEATURES = 100
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

def download_url(url: str, save_path: str, chunk_size=1024*64):
    '''
    Download a file from url

    :param url: url
    :param save_path: save_path
    :param chunk_size: chunk_size (Optional)
    '''
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)

def search_cql(prov: str, cql_filter: str, max_features = MAX_FEATURES)->list[str]:
    '''
    Download a file from url

    :param prov: prov
    :param cql_filter: cql_filter
    :param max_features: max_features
    :return: list of urls for TSG file to download
    '''
    url = NVCL_URLS.get(prov)
    params = {
              'service': 'WFS',
              'version': '1.1.0',
              'request': 'GetFeature',
              'typename': 'gsmlp:BoreholeView',
              'outputFormat': 'csv',
              'srsname': 'EPSG:4326',
              'CQL_FILTER': cql_filter,
              'maxFeatures': str(max_features)
             }
    try:
        response = request(url,params,'POST')
    except Exception as e:
        raise AuScopeCatException(
            f'Error querying data: {e}',
            500
        )
    csvBuffer = StringIO(response.text)
    df = pd.read_csv(filepath_or_buffer = csvBuffer, low_memory=False)
    urlAll = 'https://nvclstore.z8.web.core.windows.net/all.csv'
    dfA = pd.read_csv(urlAll)
    LOGGER.info((f'{prov} cql return: {df.shape[0]} : dfAll return {dfA.shape[0]}'))
    if df.shape[0] < 1:
        return []
    df = df.loc[df['gsmlp:nvclCollection']]

    urls = []
    for bhIdentifier in df['gsmlp:identifier']:
        bhIdentifier1 = bhIdentifier.split('://')[1]
        dfMask = dfA['BoreholeURI'].str.contains(bhIdentifier1, na=False, case=False, regex=False)
        dfUrls = dfA[dfMask].reset_index()
        if dfUrls.shape[0] > 0:
            url = dfUrls.loc[0,'DownloadLink']
            urls.append(url)

    LOGGER.info((f'{prov} search_cql return urls: {len(urls)}'))
    return urls

def downloadTSG(prov: str,name: str = None, bbox: str = None, kmlCoords: str = None, max_features = MAX_FEATURES)->int:
    '''
    Download TSG files with Polygon filter

    :param prov: prov
    :param cql_filter: cql_filter
    :param max_features: max_features
    :return: number of downloaded files
    '''
    urls = []
    cql_filter = ''
    if kmlCoords :
        #KML coordinates are x,y (longitude, latitude), whereas geoserver uses LatLng (or y,x / latitude, longitude).
        lonlatList = kmlCoords.split(' ')
        latlonList = []
        for lonlat in lonlatList:
            (lon,lat) = lonlat.split(',')
            latlonList.append(f'{lat} {lon}')
        latlonStr = ','.join(latlonList)
        if len(cql_filter):
            cql_filter +=  ' AND '
        cql_filter += f'INTERSECTS(gsmlp:shape,POLYGON(({latlonStr})))'

    if name :
        if len(cql_filter):
            cql_filter +=  ' AND '
        cql_filter += f'name like \'%{name}%\''

    if bbox :
        if len(cql_filter):
            cql_filter +=  ' AND '
        cql_filter += f' BBOX(gsmlp:shape,{bbox})'

    try:
        urls = downloadTSG_CQL(prov, cql_filter, max_features)
    except Exception as e:
        LOGGER.exception(f"{prov} returned error exception: {str(e)}")
        raise AuScopeCatException(
            f"Error querying data: {e}",
            500
        )
    return len(urls)

def downloadTSG_CQL(prov: str, cql_filter: str, max_features = MAX_FEATURES)->int:
    '''
    Download TSG files

    :param prov: prov
    :param cql_filter: cql_filter
    :param max_features: max_features
    :return: number of downloaded files
    '''
    if prov not in ['NT','QLD']:
        #add nvclCollection filter except NT, QLD.(exception from server)
        cql_filter += ' AND nvclCollection=\'true\''
    urls = search_cql(prov, cql_filter, max_features)
    if (max_features == 1000001):
        #if 1000001, just simulate downloading
        return urls
    for url in urls:
        fn = url.replace('/','-').replace(':','-')
        LOGGER.info((f'{prov} downloadTSG::downloaded: {fn}'))
        download_url(url,fn)
    return urls

