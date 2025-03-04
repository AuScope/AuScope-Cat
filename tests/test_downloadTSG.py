import sys
import pytest
import pandas as pd
import requests
from requests import RequestException
import tempfile
from auscopecat.downloadTSG import downloadTSG, download_url, search_cql
from auscopecat import downloadTSG as download_tsg
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
    class MockPandas():
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

def test_downloadTSG():
    pass

def test_downloadTSG_exception():
    pass

def test_downloadTSG_Polygon():
    pass

def test_downloadTSG_BBOX():
    pass

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
