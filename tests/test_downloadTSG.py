import sys
import pytest
import pandas as pd
import requests
from requests import RequestException
import tempfile
from auscopecat.downloadTSG import downloadTSG, download_url, search_cql, MAX_FEATURES
from auscopecat import downloadTSG as download_tsg
from auscopecat.auscopecat_types import AuScopeCatException
from .helpers import get_all_csv_df

def test_download_url(monkeypatch):

    class MockResponse:

        @staticmethod
        def iter_content(chunk_size=1, decode_unicode=False):
            return [b"ABC123"]

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, 'get', mock_get)
    with tempfile.NamedTemporaryFile() as fp:
        download_url("https://blah.blah", fp.name)
        fp.seek(0)
        assert fp.read() == b"ABC123"


#def test_download_url_req_exception(monkeypatch):
#
#    def mock_get(*args, **kwargs):
#        raise RequestException(*args)
#
#    monkeypatch.setattr(requests, 'get', mock_get)
#    with tempfile.NamedTemporaryFile() as fp:
#        download_url("https://blah.blah", fp.name)



def test_search_cql(monkeypatch):

    # Mocks a CSV version of https://nvclstore.z8.web.core.windows.net/all.csv
    class MockResponse:
        text = "gsmlp:nvclCollection,gsmlp:identifier\n" + \
               "true,http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8440735_11CPD005\n" + \
               "true,http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8418381_BND1\n" + \
               "true,http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8434796_YG35RD\n" + \
               "true,http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8471153_CCD09\n"


    def mock_request(url: str, params: dict = None, method:str = 'GET'):
        return MockResponse()

    monkeypatch.setattr(download_tsg, 'request', mock_request)


    # Mocks Pandas read_csv() method
    class MockPandas:
        # Keeps track of the number of times 'read_csv()' is called
        call_counter = 0

        def read_csv(filepath_or_buffer=None, low_memory=0):
            """ The first time it is called returns a Dataframe of a WFS response
                The second time it returns a Dataframe of a few rows of https://nvclstore.z8.web.core.windows.net/all.csv
            """
            if MockPandas.call_counter == 0:
                MockPandas.call_counter += 1
                # DataFrame of WFS response
                return pd.DataFrame({'gsmlp:nvclCollection': {0: True, 1: True, 2: True, 3: True}, 'gsmlp:identifier': {0: 'http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8440735_11CPD005', 1: 'http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8418381_BND1', 2: 'http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8434796_YG35RD', 3: 'http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8471153_CCD09'}})
            # DataFrame of https://nvclstore.z8.web.core.windows.net/all.csv
            return get_all_csv_df()

    # Sets the 'pd' in src/auscopecat/downloadTSG.py our 'MockPandas' class
    monkeypatch.setattr(download_tsg, 'pd', MockPandas)


    # Call 'search_cql' and check URLs
    urls = search_cql('prov', "BLAH LIKE '%BLAH%'", max_features = 30)
    assert urls == ['https://nvclstore.data.auscope.org.au/NT/8440735_11CPD005.zip',
                    'https://nvclstore.data.auscope.org.au/NT/8418381_BND1.zip',
                    'https://nvclstore.data.auscope.org.au/NT/8434796_YG35RD.zip',
                    'https://nvclstore.data.auscope.org.au/NT/8471153_CCD09.zip']


def test_search_cql_exception():
    pass


def test_downloadTSG_all(monkeypatch):
    """ Test 'downloadTSG' function with all parameters passed in
    """
    NUM_FEATURES = 5
    PROVIDER = "utopia"

    # A mock function that checks all the parameters are correct
    def mock_downloadTSG_CQL(prov: str, cql_filter: str, max_features = MAX_FEATURES):
        assert prov == PROVIDER 
        assert max_features == NUM_FEATURES
        assert cql_filter == "INTERSECTS(gsmlp:shape,POLYGON((-10.230 110.569,-9.445 155.095,-45.161 156.250,-41.021 111.027,-41.010 111.016,-10.230 110.569))) AND name like '%name%' AND BBOX(gsmlp:shape,118,-27.15,120,-27.1)"
        return ["U1", "U2", "U3"]

    # Sets the 'downloadTSG_CQL' in src/auscopecat/downloadTSG.py our 'mock_downloadTSG_CQL' function
    monkeypatch.setattr(download_tsg, 'downloadTSG_CQL', mock_downloadTSG_CQL)

    # Start the test by calling 'downloadTSG'
    url_len = downloadTSG(PROVIDER, "name", bbox="118,-27.15,120,-27.1", kmlCoords="110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230", max_features=NUM_FEATURES)
    assert url_len == 3


def test_downloadTSG_exception(monkeypatch):
    """ Test the 'downloadTSG' function where it catches an exception caught from 'downloadTSG_CQL()'
    """
    NUM_FEATURES = 5
    PROVIDER = "utopia"

    # A mock function that raises an exception
    def mock_downloadTSG_CQL(prov: str, cql_filter: str, max_features = MAX_FEATURES):
        raise Exception("Test Exception", 123)

    # Sets the 'downloadTSG_CQL' in src/auscopecat/downloadTSG.py our 'mock_downloadTSG_CQL' function
    monkeypatch.setattr(download_tsg, 'downloadTSG_CQL', mock_downloadTSG_CQL)

    # Start the test by calling 'downloadTSG' and catch the exception
    try:
        downloadTSG(PROVIDER, "name", bbox="118,-27.15,120,-27.1", kmlCoords="110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230", max_features=NUM_FEATURES)
    except AuScopeCatException as ace:
        assert ace.args == ("Error querying data: ('Test Exception', 123)",)
    else:
        assert False, "downloadTSG() failed to raise exception"


def test_downloadTSG_Polygon(monkeypatch):
    """ Test 'downloadTSG' function with polygon parameter passed in
    """
    PROVIDER = "mutopia"
    NAME = "name-ish"

    # A mock function that checks all the parameters are correct
    def mock_downloadTSG_CQL(prov: str, cql_filter: str, max_features = MAX_FEATURES):
        assert prov == PROVIDER
        assert max_features == MAX_FEATURES
        assert cql_filter == f"INTERSECTS(gsmlp:shape,POLYGON((-10.230 110.569,-9.445 155.095,-45.161 156.250,-41.021 111.027,-41.010 111.016,-10.230 110.569))) AND name like '%{NAME}%'"
        return ["U1", "U2", "U3", "U4", "U5"]

    # Sets the 'downloadTSG_CQL' in src/auscopecat/downloadTSG.py our 'mock_downloadTSG_CQL' function
    monkeypatch.setattr(download_tsg, 'downloadTSG_CQL', mock_downloadTSG_CQL)

    # Start the test by calling 'downloadTSG'
    url_len = downloadTSG(PROVIDER, NAME, kmlCoords="110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230")
    assert url_len == 5


def test_downloadTSG_BBOX(monkeypatch):
    """ Test 'downloadTSG' function with BBOX parameter passed in
    """
    PROVIDER = "utopia"
    NAME = "namely"
    BBOX = "118,-27.15,120,-27.1"

    # A mock function that checks all the parameters are correct
    def mock_downloadTSG_CQL(prov: str, cql_filter: str, max_features = MAX_FEATURES):
        assert prov == PROVIDER
        assert max_features == MAX_FEATURES
        assert cql_filter == f"name like '%{NAME}%' AND BBOX(gsmlp:shape,{BBOX})"
        return ["U1", "U2", "U3", "U4"]

    # Sets the 'downloadTSG_CQL' in src/auscopecat/downloadTSG.py our 'mock_downloadTSG_CQL' function
    monkeypatch.setattr(download_tsg, 'downloadTSG_CQL', mock_downloadTSG_CQL)

    # Start the test by calling 'downloadTSG'
    url_len = downloadTSG(PROVIDER, NAME, bbox=BBOX)
    assert url_len == 4


@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_downloadTSG_Name_live():
    resLen = downloadTSG('WA', name = '05GJD001', max_features = 1000001)
    assert (resLen == 1)
    resLen = downloadTSG('NSW', name = 'Cobbora: DM COBBORA DDH113', max_features = 1000001)
    assert (resLen == 1)
    resLen = downloadTSG('TAS', name = 'PVD001', max_features = 1000001)
    assert (resLen == 1)
    resLen = downloadTSG('NT', name = 'NTGS96/1', max_features = 1000001)
    assert (resLen == 1)
    resLen = downloadTSG('SA', name = 'KOKDD 20', max_features = 1000001)
    assert (resLen == 1)

@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_downloadTSG_Polygon_live():
    # You could use portal-clipboard to draw polygon and save as kml. then copy the coordnates to here
    # polygon test 1000001 specially for fake downloading TSG files which will consume huge resources.
    resLen = downloadTSG('TAS', kmlCoords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230', max_features= 1000001)
    assert (resLen > 300)

    resLen = downloadTSG('NSW', kmlCoords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230', max_features= 1000001)
    assert (resLen > 1000)

    resLen = downloadTSG('SA', kmlCoords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230', max_features= 1000001)
    assert (resLen > 1500)

    resLen = downloadTSG('NT', kmlCoords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230', max_features= 1000001)
    assert (resLen > 50)

    resLen = downloadTSG('QLD', kmlCoords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230', max_features= 1000001)
    assert (resLen > 400)

    resLen = downloadTSG('WA', kmlCoords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230', max_features= 1000001)
    assert (resLen > 1500)

    resLen = downloadTSG('CSIRO', kmlCoords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230', max_features= 1000001)
    assert (resLen > 3)

    resLen = downloadTSG('WA', kmlCoords= '119.037,-24.605 120.504,-24.991 119.452,-26.183 119.428,-26.181 119.037,-24.605', max_features= 1000001)
    assert (resLen > 10)

@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_downloadTSG_BBOX_live():
    # bbox test
    resLen = downloadTSG('WA', bbox= '118,-27.15,120,-27.1', max_features= 1000001)
    assert (resLen > 5)

@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_downloadTSG_Combo_live():
    # Multiple and condition test
    resLen = downloadTSG('WA',  name = '05GJD001', bbox = '110.,-44.,156,-9.', kmlCoords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230', max_features= 1000001)
    assert (resLen == 1)
