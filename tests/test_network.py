import logging

import pytest
from requests import Session

from auscopecat.auscopecat_types import AuScopeCatError

# Local imports
from auscopecat.network import request

from .helpers import make_mock_session_fn


def set_test_logger():
    """ Sets up a logger that we can use for testing output
    """
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.INFO)


@pytest.mark.parametrize("fn", [ ("get"),
                                 ("post")
                        ])
def test_request_return_200(fn, monkeypatch):
    """ Tests that error code 200, and value works for
        both "get()" and "post()"
    """
    mock_fn = make_mock_session_fn('{"123":"456"}', 200)
    monkeypatch.setattr(Session, fn, mock_fn)

    res = request("https://blah.com", {}, fn.upper())
    assert res.json()["123"] == "456"


@pytest.mark.parametrize("fn", [ ("get"),
                                 ("post")
                        ])
def test_request_return_500(fn, monkeypatch, caplog):
    """ Tests that error codes other than 200, and value works
        for both "get()" and "post()"
    """
    err_msg = "Internal Error"
    mock_fn = make_mock_session_fn(err_msg, 500)
    monkeypatch.setattr(Session, fn, mock_fn)

    request("https://blah.com", {}, fn.upper())
    assert f"returned error 500 in response: {err_msg}" in caplog.text
    caplog.clear()


@pytest.mark.parametrize("excp, message, error_code, fn",
        [
          (AuScopeCatError, "returned error exception: ", 500, "get")
        ]
    )
def test_request_exceptions(excp, message, error_code, fn, monkeypatch, caplog):
    """ Tests that networking exceptions are caught correctly
        for GET and POST operations
    """

    def mock_get_http_exc(*args, **kwargs):
        raise excp(message, error_code)

    monkeypatch.setattr(Session, fn, mock_get_http_exc)
    with pytest.raises(AuScopeCatError):
        request("https://blah.com", {}, fn.upper())

        assert message in caplog.text
        caplog.clear()


# Mark this test as failable
@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_request_live():
    params = {
              "service": "WFS",
              "version": "1.1.0",
              "request": "GetFeature",
              "typename": "gsmlp:BoreholeView",
              "outputFormat": "json",
              "FILTER": "<ogc:Filter><ogc:PropertyIsEqualTo matchCase=\"false\"><ogc:PropertyName>gsmlp:nvclCollection</ogc:PropertyName><ogc:Literal>true</ogc:Literal></ogc:PropertyIsEqualTo></ogc:Filter>",
              "maxFeatures": str(10)
             }
    with pytest.raises(AuScopeCatError):
        res = request('https://auscope.portal.org.au/api/getBlah.do')

    res = request('https://auportal-dev.geoanalytics.group/api/getKnownLayers.do')
    data = res.json()['data']
    data_len = len(data)
    assert data_len > 100

    res = request('https://geology.data.nt.gov.au/geoserver/wfs',params, 'GET')
    features = res.json()['features']
    assert len(features) == 10

    res = request('https://geology.data.nt.gov.au/geoserver/wfs',params, 'POST')
    features = res.json()['features']
    assert len(features) == 10

    res = request('https://geology.data.nt.gov.au/geoserver/wfs')
    assert res.status_code == 400


@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_request_wms_live():
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
    res = request('https://geossdi.dmp.wa.gov.au/services/ows', params, 'POST')
    img_len = len(res.content)
    assert (img_len >= 10000)


@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_request_wfs_live():
    params = {
            "service": "WFS",
            "version": "1.1.0",
            "request": "GetFeature",
            "typename": "gsmlp:BoreholeView",
            "outputFormat": "json",
            "FILTER": "<ogc:Filter><ogc:PropertyIsEqualTo matchCase=\"false\"><ogc:PropertyName>gsmlp:nvclCollection</ogc:PropertyName><ogc:Literal>true</ogc:Literal></ogc:PropertyIsEqualTo></ogc:Filter>",
            "maxFeatures": str(2)
            }
    res = request('https://geossdi.dmp.wa.gov.au/services/ows', params, 'POST')
    features = res.json()['features']
    assert (len(features) == 2)
