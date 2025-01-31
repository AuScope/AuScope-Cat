from auscopecat.network import request
import pytest

def test_request():
    params = {
              "service": "WFS",
              "version": "1.1.0",
              "request": "GetFeature",
              "typename": "gsmlp:BoreholeView",
              "outputFormat": "json",
              "FILTER": "<ogc:Filter><ogc:PropertyIsEqualTo matchCase=\"false\"><ogc:PropertyName>gsmlp:nvclCollection</ogc:PropertyName><ogc:Literal>true</ogc:Literal></ogc:PropertyIsEqualTo></ogc:Filter>",
              "maxFeatures": str(10)
             }
    res = request('https://auscope.portal.org.au/api/getBlah.do')
    assert (res == [])

    res = request('https://auportal-dev.geoanalytics.group/api/getKnownLayers.do')
    data = res.json()['data']
    dataLen = len(data)
    assert (dataLen > 100)

    res = request('https://geology.data.nt.gov.au/geoserver/wfs',params, 'GET')
    features = res.json()['features']
    assert (len(features) == 10)

    res = request('https://geology.data.nt.gov.au/geoserver/wfs',params, 'POST')
    features = res.json()['features']
    assert (len(features) == 10)

    res = request('https://geology.data.nt.gov.au/geoserver/wfs') 
    assert (res.status_code == 400)

def test_requestWMS():
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
    imgLen = len(res.content)
    assert (imgLen >= 10000)

def test_requestWFS():
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