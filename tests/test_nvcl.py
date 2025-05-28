import tempfile

import pandas as pd
import pytest
import requests

from auscopecat import api, nvcl
from auscopecat.auscopecat_types import AuScopeCatError
from auscopecat.nvcl import MAX_FEATURES, download_tsg, search_cql_tsg, search_tsg
from auscopecat.utils import download_url

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



def test_search_cql_tsg(monkeypatch):
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

        def read_csv(self, filepath_or_buffer=None, low_memory=0):
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
    urls = search_cql_tsg('prov', "BLAH LIKE '%BLAH%'", max_features = 30)
    assert urls == ['https://nvclstore.data.auscope.org.au/NT/8440735_11CPD005.zip',
                    'https://nvclstore.data.auscope.org.au/NT/8418381_BND1.zip',
                    'https://nvclstore.data.auscope.org.au/NT/8434796_YG35RD.zip',
                    'https://nvclstore.data.auscope.org.au/NT/8471153_CCD09.zip']


def test_search_cql_tsg_exception():
    pass


def test_download_tsg_all(monkeypatch):
    """ Test 'download_tsg' function with all parameters passed in
    """
    num_features = 5
    provider = "utopia"

    # A mock function that checks all the parameters are correct
    def mock_search_tsg(prov: str, name: str, bbox: str, kml_coords:str, max_features = MAX_FEATURES):
        assert prov == provider
        assert max_features == num_features
        return ["U1", "U2", "U3"]

    # Sets the 'search_tsg' in src/auscopecat/nvcl.py to our 'mock_search_tsg' function
    monkeypatch.setattr(nvcl, 'search_tsg', mock_search_tsg)

    # Start the test by calling 'download_tsg'
    urls = download_tsg(provider, name="name", bbox="118,-27.15,120,-27.1", kml_coords="110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230", max_features=num_features, simulation=True)
    assert len(urls) == 3


def test_download_tsg_exception(monkeypatch):
    """ Test the 'download_tsg' function where it catches an exception caught from 'download_tsg_cql()'
    """
    num_features = 5
    provider = "utopia"

    # A mock function that raises an exception
    def mock_search_tsg(prov: str, name: str, bbox: str, kml_coords: str, max_features = MAX_FEATURES):
        raise Exception("Test Exception", 123)

    # Sets the 'search_tsg' in src/auscopecat/nvcl.py to our 'mock_search_tsg' function
    monkeypatch.setattr(nvcl, 'search_tsg', mock_search_tsg)

    # Start the test by calling 'download_tsg' and catch the exception
    try:
        download_tsg(provider, "name", bbox="118,-27.15,120,-27.1", kml_coords="110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230", max_features=num_features)
    except AuScopeCatError as ace:
        assert ace.args == ("Error querying data: ('Test Exception', 123)",)
    else:
        assert False, "download_tsg() failed to raise exception"


def test_download_tsg_polygon(monkeypatch):
    """ Test 'download_tsg' function with polygon parameter passed in
    """
    provider = "mutopia"
    name = "name-ish"

    # A mock function that checks all the parameters are correct
    def mock_search_tsg(prov: str, name: str, bbox: str, kml_coords: str, max_features = MAX_FEATURES):
        assert prov == provider
        assert max_features == MAX_FEATURES
        return ["U1", "U2", "U3", "U4", "U5"]

    # Sets the 'search_tsg' in src/auscopecat/nvcl.py to our 'mock_search_tsg' function
    monkeypatch.setattr(nvcl, 'search_tsg', mock_search_tsg)

    # Start the test by calling 'download_tsg'
    urls = download_tsg(provider, name, kml_coords="110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230", simulation=True)
    assert len(urls) == 5


def test_download_tsg_bbox(monkeypatch):
    """ Test 'download_tsg' function with BBOX parameter passed in
    """
    provider = "utopia"
    name = "namely"
    bbox = "118,-27.15,120,-27.1"

    # A mock function that checks all the parameters are correct
    def mock_search_tsg(prov: str, name: str, bbox: str, kml_coords:str, max_features = MAX_FEATURES):
        assert prov == provider
        assert max_features == MAX_FEATURES
        return ["U1", "U2", "U3", "U4"]

    # Sets the 'search_tsg' in src/auscopecat/nvcl.py to our 'mock_search_tsg' function
    monkeypatch.setattr(nvcl, 'search_tsg', mock_search_tsg)

    # Start the test by calling 'download_tsg'
    urls = download_tsg(provider, name, bbox=bbox, simulation=True)
    assert len(urls) == 4

@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_search_tsg_name_live():
    urls = search_tsg('WA', name = '05GJD001')
    assert (len(urls) == 1)
    urls = search_tsg('NSW', name = 'Cobbora: DM COBBORA DDH113')
    assert (len(urls) == 1)
    urls = search_tsg('TAS', name = 'PVD001')
    assert (len(urls) == 1)
    urls = search_tsg('NT', name = 'NTGS96/1')
    assert (len(urls) == 1)
    urls = search_tsg('SA', name = 'KOKDD 20')
    assert (len(urls) == 1)

@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_search_tsg_polygon_live():
    # You could use portal-clipboard to draw polygon and save as kml. then copy the coordnates to here
    # polygon test 1000001 specially for fake downloading TSG files which will consume huge resources.
    urls = search_tsg('TAS', kml_coords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230')
    assert (len(urls) > 300)

    urls = search_tsg('NSW', kml_coords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230')
    assert (len(urls) > 1000)

    urls = search_tsg('SA', kml_coords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230')
    assert (len(urls) > 1500)

    urls = search_tsg('NT', kml_coords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230')
    assert (len(urls) > 50)

    urls = search_tsg('QLD', kml_coords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230')
    assert (len(urls) > 400)

    urls = search_tsg('WA', kml_coords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230')
    assert (len(urls) > 1500)

    urls = search_tsg('CSIRO', kml_coords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230')
    assert (len(urls) > 3)

    urls = search_tsg('WA', kml_coords= '119.037,-24.605 120.504,-24.991 119.452,-26.183 119.428,-26.181 119.037,-24.605')
    assert (len(urls) > 10)

@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_search_tsg_bbox_live():
    # bbox test
    urls = search_tsg('WA', bbox= '118,-27.15,120,-27.1')
    assert (len(urls) > 5)

@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_search_tsg_combo_live():
    # Multiple and condition test
    urls = search_tsg('WA',  name = '05GJD001', bbox = '110.,-44.,156,-9.', kml_coords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230')
    assert (len(urls) == 1)
    urls = download_tsg('WA',  name = '05GJD001', bbox = '110.,-44.,156,-9.', kml_coords= '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230', simulation= True)
    assert (len(urls) == 1)
