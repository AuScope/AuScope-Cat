from types import SimpleNamespace
import pytest
from auscopecat.api import download, search, validate_bbox
from auscopecat.auscopecat_types import DownloadType, ServiceType, SpatialSearchType, AuScopeCatException


VALID_BBOX = {
    "north": -24.7257367141281, "east": 131.38891993801204,
    "south": -25.793715746583374, "west": 129.77844446004175
}

INVALID_BBOX = {
    "north": "north", "east": 131.38891993801204,
    "south": -25.793715746583374, "west": 129.77844446004175
}

SEARCH_RESULT = SimpleNamespace(
    url = "https://public.lithodat.com/geoserver/wfs",
    type = "WFS",
    name = "public_data:lithodat_ft_samples"
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

def test_search_invalid_ogc_type():
    with pytest.raises(AuScopeCatException):
        search("pattern", "WXS")

def test_search_invalid_spatial_type():
    with pytest.raises(AuScopeCatException):
        search("pattern", spatial_search_type="ABOUNDS", bbox=VALID_BBOX)

def test_search_with_invalid_bbox():
    with pytest.raises(AuScopeCatException):
        search("pattern", spatial_search_type=SpatialSearchType.INTERSECTS, bbox=INVALID_BBOX)

def test_successful_wfs_search():
    try:
        search("flinders", ServiceType.WFS)
    except AuScopeCatException as e:
        assert False, f"Error searching: {e}"

def test_download_invalid_download_type():
    with pytest.raises(AuScopeCatException):
        download(SEARCH_RESULT, "XLSX")

def test_download_missing_bbox():
    with pytest.raises(AuScopeCatException):
        download(SEARCH_RESULT, DownloadType.CSV)
