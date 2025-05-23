import pytest
import pandas as pd
import requests
import tempfile
from auscopecat.nvcl import downloadTSG, search_TSG, search_cql_TSG, MAX_FEATURES
from auscopecat.utils import download_url
from auscopecat import nvcl, api
from auscopecat.auscopecat_types import AuScopeCatException
from .helpers import get_all_csv_df

def test_download_url(monkeypatch):

    # This mocks the requests package 'Response' class
    class MockResponse:

        @staticmethod
        def iter_content(chunk_size=1, decode_unicode=False):
            return [b"ABC123"]

    # This mocks the requests package 'get' function, returning a 'MockResponse'
    def mock_get(*args, **kwargs):
        return MockResponse()

    # Overwrite the requests package 'get' function
    monkeypatch.setattr(requests, 'get', mock_get)

    # Call 'download_url' confirm that the file has correct content passed in by the mocking class
    with tempfile.NamedTemporaryFile(delete=False) as fp:
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



def test_search_cql_TSG(monkeypatch):
    """ Tests 'search_cql_TSG" function 
        'search_cql_TSG' make three function calls to external network resources
        These functions are mocked to ensure that this test will run independently of network resources
    """

    # Mocks by returning a CSV version of https://nvclstore.z8.web.core.windows.net/all.csv
    class MockResponse:
        text = "gsmlp:nvclCollection,gsmlp:identifier\n" + \
               "true,http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8440735_11CPD005\n" + \
               "true,http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8418381_BND1\n" + \
               "true,http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8434796_YG35RD\n" + \
               "true,http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8471153_CCD09\n"

    def mock_request(url: str, params: dict = None, method:str = 'GET'):
        return MockResponse()

    # Sets the 'request' in src/auscopecat/nvcl.py to our 'mock_request' class
    monkeypatch.setattr(api, 'request', mock_request)

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
                # First call - return DataFrame of WFS response
                return pd.DataFrame({
                    'gsmlp:nvclCollection': {
                        0: True,
                        1: True,
                        2: True,
                        3: True
                    },
                    'gsmlp:identifier': {
                        0: 'http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8440735_11CPD005',
                        1: 'http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8418381_BND1',
                        2: 'http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8434796_YG35RD',
                        3: 'http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8471153_CCD09'
                    },
                    'BoreholeURI': {
                        0:'http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8440735_11CPD005',
                        1:'http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8418381_BND1',
                        2:'http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8434796_YG35RD',
                        3:'http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8471153_CCD09'
                    },
                    'DownloadLink': {
                        0:'https://nvclstore.data.auscope.org.au/NT/8440735_11CPD005.zip',
                        1:'https://nvclstore.data.auscope.org.au/NT/8418381_BND1.zip',
                        2:'https://nvclstore.data.auscope.org.au/NT/8434796_YG35RD.zip',
                        3:'https://nvclstore.data.auscope.org.au/NT/8471153_CCD09.zip'
                    }
                })
            # Second call - return DataFrame of https://nvclstore.z8.web.core.windows.net/all.csv
            return get_all_csv_df()

    # Sets the 'pd' in src/auscopecat/nvcl.py to our 'MockPandas' class
    monkeypatch.setattr(nvcl, 'pd', MockPandas)

    # Call 'search_cql_TSG' and check URLs
    urls = search_cql_TSG('prov', "BLAH LIKE '%BLAH%'", max_features = 30)
    assert urls == ['https://nvclstore.data.auscope.org.au/NT/8440735_11CPD005.zip',
                    'https://nvclstore.data.auscope.org.au/NT/8418381_BND1.zip',
                    'https://nvclstore.data.auscope.org.au/NT/8434796_YG35RD.zip',
                    'https://nvclstore.data.auscope.org.au/NT/8471153_CCD09.zip']


def test_search_cql_TSG_exception():
    pass


def test_downloadTSG_all(monkeypatch):
    """ Test 'downloadTSG' function with all parameters passed in
    """
    NUM_FEATURES = 5
    PROVIDER = "utopia"

    # A mock function that checks all the parameters are correct
    def mock_search_TSG(prov: str, name: str, bbox: str, kmlCoords:str, max_features = MAX_FEATURES):
        assert prov == PROVIDER 
        assert max_features == NUM_FEATURES
        return ["U1", "U2", "U3"]

    # Sets the 'search_TSG' in src/auscopecat/nvcl.py to our 'mock_search_TSG' function
    monkeypatch.setattr(nvcl, 'search_TSG', mock_search_TSG)

    # Start the test by calling 'downloadTSG'
    urls = downloadTSG(PROVIDER, name="name", bbox="118,-27.15,120,-27.1", kmlCoords="110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230", max_features=NUM_FEATURES,simulation=True)
    assert len(urls) == 3


def test_downloadTSG_exception(monkeypatch):
    """ Test the 'downloadTSG' function where it catches an exception caught from 'downloadTSG_CQL()'
    """
    NUM_FEATURES = 5
    PROVIDER = "utopia"

    # A mock function that raises an exception
    def mock_search_TSG(prov: str, name: str, bbox: str, kmlCoords:str, max_features = MAX_FEATURES):
        raise Exception("Test Exception", 123)

    # Sets the 'search_TSG' in src/auscopecat/nvcl.py to our 'mock_search_TSG' function
    monkeypatch.setattr(nvcl, 'search_TSG', mock_search_TSG)

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
    def mock_search_TSG(prov: str, name: str, bbox: str, kmlCoords:str, max_features = MAX_FEATURES):
        assert prov == PROVIDER
        assert max_features == MAX_FEATURES
        return ["U1", "U2", "U3", "U4", "U5"]

    # Sets the 'search_TSG' in src/auscopecat/nvcl.py to our 'mock_search_TSG' function
    monkeypatch.setattr(nvcl, 'search_TSG', mock_search_TSG)

    # Start the test by calling 'downloadTSG'
    urls = downloadTSG(PROVIDER, NAME, kmlCoords="110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230",simulation=True)
    assert len(urls) == 5


def test_downloadTSG_BBOX(monkeypatch):
    """ Test 'downloadTSG' function with BBOX parameter passed in
    """
    PROVIDER = "utopia"
    NAME = "namely"
    BBOX = "118,-27.15,120,-27.1"

    # A mock function that checks all the parameters are correct
    def mock_search_TSG(prov: str, name: str, bbox: str, kmlCoords:str, max_features = MAX_FEATURES):
        assert prov == PROVIDER
        assert max_features == MAX_FEATURES
        return ["U1", "U2", "U3", "U4"]

    # Sets the 'search_TSG' in src/auscopecat/nvcl.py to our 'mock_search_TSG' function
    monkeypatch.setattr(nvcl, 'search_TSG', mock_search_TSG)

    # Start the test by calling 'downloadTSG'
    urls = downloadTSG(PROVIDER, NAME, bbox=BBOX,simulation=True)
    assert len(urls) == 4

@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_search_TSG_Name_live():
    urls = search_TSG('WA', name = '05GJD001')
    assert (len(urls) == 1)
    urls = search_TSG('NSW', name = 'Cobbora: DM COBBORA DDH113')
    assert (len(urls) == 1)
    urls = search_TSG('TAS', name = 'PVD001')
    assert (len(urls) == 1)
    urls = search_TSG('NT', name = 'NTGS96/1')
    assert (len(urls) == 1)
    urls = search_TSG('SA', name = 'KOKDD 20')
    assert (len(urls) == 1)

@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_search_TSG_Polygon_live():
    # You could use portal-clipboard to draw polygon and save as kml. then copy the coordnates to here
    # polygon test 1000001 specially for fake downloading TSG files which will consume huge resources.
    urls = search_TSG('TAS', kmlCoords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230')
    assert (len(urls) > 300)

    urls = search_TSG('NSW', kmlCoords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230')
    assert (len(urls) > 1000)

    urls = search_TSG('SA', kmlCoords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230')
    assert (len(urls) > 1500)

    urls = search_TSG('NT', kmlCoords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230')
    assert (len(urls) > 50)

    urls = search_TSG('QLD', kmlCoords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230')
    assert (len(urls) > 400)

    urls = search_TSG('WA', kmlCoords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230')
    assert (len(urls) > 1500)

    urls = search_TSG('CSIRO', kmlCoords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230')
    assert (len(urls) > 3)

    urls = search_TSG('WA', kmlCoords= '119.037,-24.605 120.504,-24.991 119.452,-26.183 119.428,-26.181 119.037,-24.605')
    assert (len(urls) > 10)

@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_search_TSG_BBOX_live():
    # bbox test
    urls = search_TSG('WA', bbox= '118,-27.15,120,-27.1')
    assert (len(urls) > 5)

@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_search_TSG_Combo_live():
    # Multiple and condition test
    urls = search_TSG('WA',  name = '05GJD001', bbox = '110.,-44.,156,-9.', kmlCoords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230')
    assert (len(urls) == 1)
    urls = downloadTSG('WA',  name = '05GJD001', bbox = '110.,-44.,156,-9.', kmlCoords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230', simulation= True)
    assert (len(urls) == 1)
