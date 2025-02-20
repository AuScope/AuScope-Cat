from types import SimpleNamespace
import pytest
from auscopecat.api import download, search, wfs_get_feature, validate_bbox
from auscopecat.auscopecat_types import DownloadType, ServiceType, SpatialSearchType, AuScopeCatException


VALID_BBOX = {
    "north": -22.19, "east": 123.07,
    "south": -28.00, "west": 115.56
}

INVALID_BBOX = {
    "north": "north", "east": 131.38891993801204,
    "south": -25.793715746583374, "west": 129.77844446004175
}

SEARCH_RESULT = SimpleNamespace(
    url = "https://geossdi.dmp.wa.gov.au/services/wfs",
    type = "WFS",
    name = "gsmlp:BoreholeView"
)

# bbox tests
def test_valid_bbox():
    try:
        validate_bbox(VALID_BBOX)
    except AuScopeCatException as e:
        assert False, f"Error validating bbox: {e}"

def test_invalid_bbox():
    with pytest.raises(AuScopeCatException):
        validate_bbox(INVALID_BBOX)

# search tests
def test_search_invalid_ogc_type():
    with pytest.raises(AuScopeCatException):
        search("pattern", "WXS")

def test_search_invalid_spatial_type():
    with pytest.raises(AuScopeCatException):
        search("pattern", spatial_search_type="ABOUNDS", bbox=VALID_BBOX)

def test_search_with_invalid_bbox():
    with pytest.raises(AuScopeCatException):
        search("pattern", spatial_search_type=SpatialSearchType.INTERSECTS, bbox=INVALID_BBOX)

@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_successful_wfs_search():
    try:
        search_result = search("nvcl", ServiceType.WFS)
        assert(len(search_result) > 0)
        for result in search_result:
            assert(hasattr(result, "name"))
            assert(hasattr(result, "type"))
            assert(hasattr(result, "url"))
    except AuScopeCatException as e:
        assert False, f"Error searching: {e}"

# wfs_get_festure tests
def test_wfs_get_feature_invalid_bbox():
    with pytest.raises(AuScopeCatException):
        wfs_get_feature(SEARCH_RESULT.url, SEARCH_RESULT.name, INVALID_BBOX)

@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_wfs_get_feature_success():
    response = wfs_get_feature(SEARCH_RESULT.url, SEARCH_RESULT.name, VALID_BBOX, max_features = 10)
    assert(response.status_code == 200)
    # 10 features + CSV header = 11 lines
    assert(response.content.count(b"\n") == 11)

# download tests
def test_download_invalid_download_type():
    with pytest.raises(AuScopeCatException):
        download(SEARCH_RESULT, "XLSX")

def test_download_missing_bbox():
    with pytest.raises(AuScopeCatException):
        download(SEARCH_RESULT, DownloadType.CSV)

def test_download_invalid_bbox():
    with pytest.raises(AuScopeCatException):
        download(SEARCH_RESULT, DownloadType.CSV, bbox=INVALID_BBOX)

def test_download_invalid_srs():
    with pytest.raises(AuScopeCatException):
        download(SEARCH_RESULT, DownloadType.CSV, bbox=INVALID_BBOX, srs_name="ESPG:4326")

@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_successful_download(mocker):
    try:
        mock_file = mocker.mock_open()
        mocker.patch("builtins.open", mock_file)
        download(SEARCH_RESULT, DownloadType.CSV, VALID_BBOX, "EPSG:4236", 10, file_name="test_download.csv")
        mock_file.assert_called_once_with("test_download.csv", "wb")
    except AuScopeCatException as e:
        assert False, f"Error downloading: {e}"

# combined tests
@pytest.mark.xfail(reason="Testing live servers is not reliable as they are sometimes unavailable")
def test_search_and_download(mocker):
    try:
        search_result = search("nvcl", ServiceType.WFS)
        mock_file = mocker.mock_open()
        mocker.patch("builtins.open", mock_file)
        if search_result is not None and len(search_result) > 0:
            download(search_result[0], DownloadType.CSV, VALID_BBOX, "EPSG:4236", 5, file_name="test_download.csv")
            mock_file.assert_called_once_with("test_download.csv", "wb")
        else:
            assert False, "No search results to download"
    except AuScopeCatException as e:
        assert False, f"Error downloading: {e}"
