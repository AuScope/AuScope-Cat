import logging
import sys
from auscopecat.auscopecat_types import AuScopeCatException
from auscopecat.api import search_cql, MAX_FEATURES
from auscopecat.utils import download_url
import pandas as pd
from pandas import DataFrame
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

def search_cql_TSG(prov: str, cql_filter: str, max_features = MAX_FEATURES)->list[str]:
    '''
    Search TSG files by CQL

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
        df = search_cql(url, params)
    except Exception as e:
        raise AuScopeCatException(
            f'Error querying data: {e}',
            500
        )

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

def get_cql_filter(layerName:str, geometryName:str, name: str = None, bbox: str = None, kmlCoords: str = None, max_features = MAX_FEATURES, isNvcl = False, prov: str = None)->str:
    cql_filter = ''
    if kmlCoords :
        #KML coordinates are x,y (longitude, latitude), whereas geoserver uses LatLng (or y,x / latitude, longitude).
        lonlatList = kmlCoords.split(' ')
        latlonList = []
        for lonlat in lonlatList:
            (lon,lat) = lonlat.split(',')
            latlonList.append(f'{lat} {lon}')
        latlonStr = ','.join(latlonList)
        if cql_filter.strip() != "":
            cql_filter +=  ' AND '
        cql_filter += f'INTERSECTS({geometryName},POLYGON(({latlonStr})))'

    if name :
        if cql_filter.strip() != "":
            cql_filter +=  ' AND '
        cql_filter += f'name like \'%{name}%\''

    if bbox :
        if cql_filter.strip() != "":
            cql_filter +=  ' AND '
        cql_filter += f'BBOX({geometryName},{bbox})'

    if isNvcl and prov not in ['NT','QLD']:
        #add nvclCollection filter except NT, QLD.(exception from server)
        cql_filter += ' AND nvclCollection=\'true\''
    return cql_filter

def get_cql_params(layerName:str, geometryName:str, name: str = None, bbox: str = None, kmlCoords: str = None, max_features = MAX_FEATURES, isNvcl = False, prov: str = None)->dict:
    cql_filter = get_cql_filter(layerName, geometryName, name, bbox, kmlCoords, max_features, True, prov)
    cql_params = {
              'service': 'WFS',
              'version': '1.1.0',
              'request': 'GetFeature',
              'typename': layerName,
              'outputFormat': 'csv',
              'srsname': 'EPSG:4326',
              'CQL_FILTER': cql_filter,
              'maxFeatures': str(max_features)
             }
    return cql_params

def add_tsg_urls(prov:str, df:DataFrame)->any:
    urlAll = 'https://nvclstore.z8.web.core.windows.net/all.csv'
    dfA = pd.read_csv(urlAll)
    LOGGER.info((f'{prov} cql return: {df.shape[0]} : dfAll return {dfA.shape[0]}'))
    if df.shape[0] < 1:
        return []
    df = df.loc[df['gsmlp:nvclCollection']]
    df['DownloadLink'] = ''
    for index,bhIdentifier in enumerate(df['gsmlp:identifier']):
        bhIdentifier1 = bhIdentifier.split('://')[1]
        dfMask = dfA['BoreholeURI'].str.contains(bhIdentifier1, na=False, case=False, regex=False)
        dfUrls = dfA[dfMask].reset_index()
        if dfUrls.shape[0] > 0:
            df.loc[index,'DownloadLink'] = dfUrls.loc[0,'DownloadLink']
    return df

def search_cql_TSG_df(prov: str,name: str = None, bbox: str = None, kmlCoords: str = None, max_features = MAX_FEATURES)->any:
    '''
    search TSG files with filters

    :param prov: prov
    :param name: name
    :param bbox: bbox
    :param kmlCoords: kmlCoords
    :param max_features: max_features
    :return: dataframe
    '''

    cql_params = get_cql_params('gsmlp:BoreholeView','gsmlp:shape',name, bbox, kmlCoords, max_features,True,prov)
    url = NVCL_URLS.get(prov)
    try:
        df = search_cql(url, cql_params)
    except Exception as e:
        raise AuScopeCatException(
            f'Error querying data: {e}',
            500
        )
    LOGGER.info((f'{prov} search_cql return records0: {df.shape[0]}'))
    df = add_tsg_urls(prov,df)
    LOGGER.info((f'{prov} search_cql return records: {df.shape[0]}'))
    return df

def downloadTSG(prov: str,name: str = None, bbox: str = None, kmlCoords: str = None, max_features = MAX_FEATURES, simulation: bool = False) -> list[str]:
    '''
    Download TSG files with Polygon filter

    :param prov: prov
    :param name: name
    :param bbox: bbox
    :param kmlCoords: kmlCoords
    :param max_features: max_features
    :param simulation: simulation
    :return: a list of url of downloaded TSG files
    '''
    urls = []

    try:
        urls = search_TSG(prov, name, bbox, kmlCoords, max_features)
        for url in urls:
            fn = url.replace('/','-').replace(':','-')
            LOGGER.info((f'{prov} downloadTSG::downloaded: {fn}'))
            if (not simulation):
                download_url(url,fn)

    except Exception as e:
        LOGGER.exception(f"{prov} returned error exception: {str(e)}")
        raise AuScopeCatException(
            f"Error querying data: {e}",
            500
        )
    return urls

def search_TSG(prov: str, name: str = None, bbox: str = None, kmlCoords: str = None,  max_features = MAX_FEATURES) -> list[str]:
    '''
    search TSG files with filter

    :param prov: prov
    :param name: name
    :param bbox: bbox
    :param kmlCoords: kmlCoords
    :param max_features: max_features
    :return: a list of url of TSG files
    '''
    cql_filter = get_cql_filter('gsmlp:BoreholeView', 'gsmlp:shape', name, bbox, kmlCoords, max_features, True, prov)
    urls = search_cql_TSG(prov, cql_filter, max_features)
    return urls
