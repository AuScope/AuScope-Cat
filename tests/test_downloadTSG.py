import pytest
from auscopecat.downloadTSG import search_TSG, downloadTSG
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