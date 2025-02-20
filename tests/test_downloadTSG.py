import pytest
from auscopecat.downloadTSG import downloadTSG_BBOX, downloadTSG_Name, downloadTSG_Polygon
@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_downloadTSG_Name_live():

    resLen = downloadTSG_Name('WA', '05GJD001', 1000001)
    assert (resLen == 1)
    resLen = downloadTSG_Name('NSW', 'Cobbora: DM COBBORA DDH113', 1000001)
    assert (resLen == 1)
    resLen = downloadTSG_Name('TAS', 'PVD001', 1000001)
    assert (resLen == 1)
    resLen = downloadTSG_Name('NT', 'NTGS96/1', 1000001)
    assert (resLen == 1)
    resLen = downloadTSG_Name('SA', 'KOKDD 20', 1000001)
    assert (resLen == 1)

@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_downloadTSG_Polygon_live():
    # You could use portal-clipboard to draw polygon and save as kml. then copy the coordnates to here
    # polygon test 1000001 specially for fake downloading TSG files which will consume huge resources.
    resLen = downloadTSG_Polygon('TAS', '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230', 1000001)
    assert (resLen > 300)

    resLen = downloadTSG_Polygon('NSW', '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230', 1000001)
    assert (resLen > 1000)

    resLen = downloadTSG_Polygon('SA', '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230', 1000001)
    assert (resLen > 1500)

    resLen = downloadTSG_Polygon('NT', '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230', 1000001)
    assert (resLen > 50)

    resLen = downloadTSG_Polygon('QLD', '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230', 1000001)
    assert (resLen > 400)

    resLen = downloadTSG_Polygon('WA', '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230', 1000001)
    assert (resLen > 1500)

    resLen = downloadTSG_Polygon('CSIRO', '110.569,-10.230 155.095,-9.445 156.250,-45.161 111.027,-41.021 111.016,-41.010 110.569,-10.230', 1000001)
    assert (resLen > 3)

    resLen = downloadTSG_Polygon('WA', '119.037,-24.605 120.504,-24.991 119.452,-26.183 119.428,-26.181 119.037,-24.605', 1000001)
    assert (resLen > 10)

@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_downloadTSG_BBOX_live():
    # bbox test
    resLen = downloadTSG_BBOX('WA', '118,-27.15,120,-27.1', 1000001)
    assert (resLen > 5)
