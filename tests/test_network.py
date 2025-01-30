from auscopecat.network import request, requestWMS, requestWFS
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

    res = request('https://geology.data.nt.gov.au/geoserver/wfs',params, 'GET')
    features = res.json()['features']
    assert (len(features) == 10)

    res = request('https://geology.data.nt.gov.au/geoserver/wfs',params, 'POST')
    features = res.json()['features']
    assert (len(features) == 10)

    res = request('https://geology.data.nt.gov.au/geoserver/wfs') 
    assert (res.status_code == 400)
    
def test_requestWMS():
    res = requestWMS('https://geossdi.dmp.wa.gov.au/services/ows')
    imgLen = len(res.content)
    assert (imgLen >= 10000)

def test_requestWFS():
    res = requestWFS('https://geossdi.dmp.wa.gov.au/services/ows')
    features = res.json()['features']
    assert (len(features) == 10)

