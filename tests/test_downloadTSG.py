import pytest
from auscopecat.downloadTSG import downloadTSG
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
