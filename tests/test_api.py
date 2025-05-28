from types import SimpleNamespace

import pytest
from requests import Response

from auscopecat.api import (
    _validate_search_inputs,
    _wfs_get_feature,
    download,
    search,
    search_records,
)
from auscopecat.auscopecat_types import (
    AuScopeCatError,
    DownloadType,
    ServiceType,
    SpatialSearchType,
)
from auscopecat.utils import validate_bbox, validate_polygon

VALID_BBOX = {
    "north": -22.19, "east": 123.07,
    "south": -28.00, "west": 115.56
}

VALID_POLYGON = [[-32.0, 125.0], [-35.0, 128.0], [-32.0, 131.0], [-32.0, 125.0]]

SEARCH_RESULT = SimpleNamespace(
    url = "https://geossdi.dmp.wa.gov.au/services/wfs",
    type = "WFS",
    name = "gsmlp:BoreholeView"
)

# bbox tests
def test_validate_bbox():
    # Valid bbox
    try:
        validate_bbox(VALID_BBOX)
    except AuScopeCatError as e:
        assert False, f"Error validating bbox: {e}"
    # String value for north
    bbox = VALID_BBOX.copy()
    bbox["north"] = "north"
    with pytest.raises(AuScopeCatError):
        validate_bbox(bbox)
    # Out of range value for north (> 90.0)
    bbox = VALID_BBOX.copy()
    bbox["north"] = 91.0
    with pytest.raises(AuScopeCatError):
        validate_bbox(bbox)
    # Out of range value for north, but adjust it
    bbox = validate_bbox(bbox, True)
    assert bbox.get("north") == 90.0

# polygon tests
def test_validate_polygon():
    try:
        validate_polygon(VALID_POLYGON)
    except AuScopeCatError as e:
        assert False, f"Error validating polygon: {e}"

# search tests
def test_validate_search_inputs():
    pattern = "test"
    ogc_types = [ServiceType.WFS]
    spatial_search_type = SpatialSearchType.INTERSECTS
    bbox = {"north": -31.456, "east": 129.653, "south": -32.456, "west": 128.653}
    try:
        _validate_search_inputs(pattern, ogc_types, spatial_search_type, bbox)
    except AuScopeCatError:
        pytest.fail("validate_search_inputs() raised AuScopeCatError")

def test_search_invalid_ogc_type():
    with pytest.raises(AuScopeCatError):
        search("pattern", "WXS")

def test_search_invalid_spatial_type():
    with pytest.raises(AuScopeCatError):
        search("pattern", spatial_search_type="ABOUNDS", bbox=VALID_BBOX)

def test_search_with_invalid_bbox():
    bbox = VALID_BBOX.copy()
    bbox["north"] = "x"
    with pytest.raises(AuScopeCatError):
        search("pattern", spatial_search_type=SpatialSearchType.INTERSECTS, bbox=bbox)

@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_successful_wfs_search():
    try:
        search_result = search("nvcl", [ServiceType.WFS])
        assert isinstance(search_result, list)
        for result in search_result:
            assert hasattr(result, "name")
            assert hasattr(result, "type")
            assert hasattr(result, "url")
    except AuScopeCatError as e:
        assert False, f"Error searching: {e}"

# wfs_get_festure tests
def test_wfs_get_feature_invalid_bbox():
    bbox = VALID_BBOX.copy()
    bbox["north"] = "x"
    with pytest.raises(AuScopeCatError):
        _wfs_get_feature(SEARCH_RESULT.url, SEARCH_RESULT.name, bbox)

@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_wfs_get_feature_success():
    response = _wfs_get_feature(SEARCH_RESULT.url, SEARCH_RESULT.name, VALID_BBOX, max_features = 10)
    assert isinstance(response, Response)
    assert response.status_code == 200
    # 10 features + CSV header = 11 lines
    assert response.content.count(b"\n") == 11

# download tests
def test_download_invalid_download_type():
    with pytest.raises(AuScopeCatError):
        download(SEARCH_RESULT, "XLSX")

def test_download_missing_bbox():
    with pytest.raises(AuScopeCatError):
        download(SEARCH_RESULT, DownloadType.CSV)

def test_download_invalid_bbox():
    bbox = VALID_BBOX.copy()
    bbox["north"] = "x"
    with pytest.raises(AuScopeCatError):
        download(SEARCH_RESULT, DownloadType.CSV, bbox=bbox)

@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_successful_download(mocker):
    try:
        mock_file = mocker.mock_open()
        mocker.patch("builtins.open", mock_file)
        download(SEARCH_RESULT, DownloadType.CSV, VALID_BBOX, "EPSG:4236", 10,
                 file_name="test_download.csv")
        mock_file.assert_called_once_with("test_download.csv", "wb")
    except AuScopeCatError as e:
        assert False, f"Error downloading: {e}"

@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_successful_download_string_params(mocker):
    try:
        mock_file = mocker.mock_open()
        mocker.patch("builtins.open", mock_file)
        download(SEARCH_RESULT, "csv", VALID_BBOX, "EPSG:4236", 10,
                 file_name="test_download.csv")
        mock_file.assert_called_once_with("test_download.csv", "wb")
    except AuScopeCatError as e:
        assert False, f"Error downloading: {e}"

# combined tests
@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_search_and_download(mocker):
    try:
        search_result = search("flinders", [ServiceType.WFS])
        mock_file = mocker.mock_open()
        mocker.patch("builtins.open", mock_file)
        if search_result is not None and len(search_result) > 0:
            download(search_result[0], DownloadType.CSV, VALID_BBOX,
                     "EPSG:4236", 5, file_name="test_download.csv")
            mock_file.assert_called_once_with("test_download.csv", "wb")
        else:
            assert False, "No search results to download"
    except AuScopeCatError as e:
        assert False, f"Error downloading: {e}"

# search_record tests
@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_search_records():
    pattern = "flinders"
    ogc_types = [ServiceType.WFS]
    spatial_search_type = SpatialSearchType.INTERSECTS
    results = search_records(pattern, ogc_types, spatial_search_type, VALID_BBOX)
    assert isinstance(results, list)
    for result in results:
        assert isinstance(result, SimpleNamespace)
        assert hasattr(result, 'id')
        assert hasattr(result, 'name')
        assert hasattr(result, 'description')
        assert hasattr(result, 'record_info_url')
        assert hasattr(result, 'constraints')
        assert hasattr(result, 'use_limit_constraints')
        assert hasattr(result, 'access_constraints')
        assert hasattr(result, 'date')
        assert hasattr(result, 'geographic_elements')
        assert hasattr(result, 'online_resources')

# search_record tests with string ogc and spatial type
pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_search_records_string_params():
    pattern = "flinders"
    ogc_types = ["wfs"]
    spatial_search_type = "intersects"
    results = search_records(pattern, ogc_types, spatial_search_type, VALID_BBOX)
    assert isinstance(results, list)
    for result in results:
        assert isinstance(result, SimpleNamespace)
        assert hasattr(result, 'id')
        assert hasattr(result, 'name')
        assert hasattr(result, 'description')
        assert hasattr(result, 'record_info_url')
        assert hasattr(result, 'constraints')
        assert hasattr(result, 'use_limit_constraints')
        assert hasattr(result, 'access_constraints')
        assert hasattr(result, 'date')
        assert hasattr(result, 'geographic_elements')
        assert hasattr(result, 'online_resources')

# Search records using polygon
@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_search_records_polygon():
    pattern = "flinders"
    ogc_types = [ServiceType.WFS]
    spatial_search_type = SpatialSearchType.INTERSECTS
    results = search_records(pattern, ogc_types=ogc_types,
                             spatial_search_type=spatial_search_type, polygon=VALID_POLYGON)
    assert isinstance(results, list)
    for result in results:
        assert isinstance(result, SimpleNamespace)
        assert hasattr(result, 'id')
        assert hasattr(result, 'name')
        assert hasattr(result, 'description')
        assert hasattr(result, 'record_info_url')
        assert hasattr(result, 'constraints')
        assert hasattr(result, 'use_limit_constraints')
        assert hasattr(result, 'access_constraints')
        assert hasattr(result, 'date')
        assert hasattr(result, 'geographic_elements')
        assert hasattr(result, 'online_resources')
