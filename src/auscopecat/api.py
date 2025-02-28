import numbers
from auscopecat.auscopecat_types import AuScopeCatException, DownloadType, ServiceType, SpatialSearchType
from auscopecat.network import request
from requests import Response
from types import SimpleNamespace


API_URL = "https://portal.auscope.org/api/"
#API_URL = "http://localhost:8080/api/"
SEARCH_URL = "searchCSWRecords.do"


def search(pattern: str, ogc_type: ServiceType = None, spatial_search_type: SpatialSearchType = None,
           bbox: dict = None) -> list[SimpleNamespace]:
    """
    Searches catalogue for services

    :param pattern: search for this string
    :param ogc_type: search for a certain kind of OGC service (Optional)
    :param bbox: the bounding box for the search data e.g. {"north":-31.456, "east":129.653...}
    :return: a list of SimpleNamespace objects with "url", "type" and "wfs_typename" attributes
    """
    if pattern is None or pattern == "":
        raise AuScopeCatException(
            "Parameter pattern can not be empty",
            500
        )
    if ogc_type and not isinstance(ogc_type, ServiceType):
        raise AuScopeCatException(
            f"Unknown service type: {ogc_type}",
            500
        )

    if spatial_search_type and bbox:
        if not isinstance(spatial_search_type, SpatialSearchType):
            raise AuScopeCatException(
                f"Unknown spatial search type: {spatial_search_type}",
                500
            )
        try:
            validate_bbox(bbox)
        except Exception:
            raise

    # Build search query
    search_query = f"{API_URL}{SEARCH_URL}?query={pattern}"

    # TODO: include multiple services
    if ogc_type is not None and ogc_type != "":
        search_query += f"&ogcServices={ogc_type.value}"

    if spatial_search_type and bbox:
        search_query += f'&spatialRelation={spatial_search_type.value}' \
                f'&westBoundLongitude={bbox.get("west")}&eastBoundLongitude={bbox.get("east")}' \
                f'&southBoundLatitude={bbox.get("south")}&northBoundLatitude={bbox.get("north")}'

    try:
        search_request = request(search_query)
    except AuScopeCatException as e:
        raise

    search_results = []
    if search_request.status_code == 200:
        results_json = search_request.json()
        if results_json.get("data") and results_json.get("data").get("totalCSWRecordHits") > 0:
            for result in results_json.get("data").get("cswRecords"):
                if result.get("onlineResources"):
                    for online_resource in result.get("onlineResources"):
                        if ogc_type is None or online_resource.get("type").lower() == ogc_type.value.lower():
                            search_results.append(SimpleNamespace(
                                   url = online_resource.get("url"),
                                   type = online_resource.get("type"),
                                   name = online_resource.get("name")
                            ))

    return search_results


def wfs_get_feature(url: str, type_name: str, bbox: dict, version = "1.1.0", srs_name: str = "EPSG:4326",
                         output_format = "csv", max_features = None) -> Response:
    if bbox is None:
        raise AuScopeCatException(
            "A bounding box (bbox) must be specified",
            500
        )
    try:
        validate_bbox(bbox)
    except Exception:
        raise

    bbox_param = f'{bbox.get("south")},{bbox.get("west")},{bbox.get("north")},{bbox.get("east")}'

    request_params = dict(
        service="wfs",
        version=version,
        request="GetFeature",
        typeNames=type_name,
        srsName=srs_name,
        bbox=bbox_param,
        outputFormat="csv"
    )

    if max_features is not None:
        request_params["maxFeatures"] = max_features

    try:
        response = request(url, request_params)
        return response
    except Exception as e:
        raise


def download(obj: SimpleNamespace, download_type: DownloadType, bbox: dict = None, srs_name: str = "EPSG:4326",
             max_features = None, version = "1.1.0", file_name: str = "download.csv") -> any:
    """
    Downloads data from object

    :param obj: SimpleNamespace objects with "url", "type" and "name" attributes
    :param download_type: type of download
    :param bbox: the bounding box for the download data e.g. {"north":-31.456, "east":129.653...}
    :param srs_name: the SRS name, e.g. "EPGS:4326" (Optional)
    :param max_features: maximum number of features to return (Optional)
    :param version: WFS version, e.g. "1.1.0" (Optional)
    :param file_name: the file name for the download (Optional)
    :return: CSV dataclear
    """
    if download_type and not isinstance(download_type, DownloadType):
        raise AuScopeCatException(
            "Unsupported download type",
            500
        )
    if bbox is None:
        raise AuScopeCatException(
            "A bounding box (bbox) must be specified",
            500
        )
    try:
        validate_bbox(bbox)
    except Exception:
        raise
    # TODO: Check to see if zip file, or append .zip if no extension
    if file_name and file_name == "":
        raise AuScopeCatException(
            "If file_name is specified it cannot be empty",
            500
        )

    if download_type is None:
        download_type = DownloadType.CSV

    try:
        response = wfs_get_feature(obj.url, obj.name, bbox, version = version, srs_name = srs_name,
                         output_format = "csv", max_features = max_features)
        if response and response.status_code and response.status_code == 200:
            f_name = "download.csv" if not file_name else file_name
            with open(f_name, "wb") as f:
                f.write(response.content)
        else:
            raise AuScopeCatException(
                f"Error downloading data: {response.reason}",
                response.status_code
            )
    except AuScopeCatException as e:
        raise


def validate_bbox(bbox: dict):
    """
    Validate a bounding box
    :param bbox: the bounding box, a dict with "north", "south", "east" and "west" keys
    """
    if (bbox.get("north") is None or not isinstance(bbox.get("north"), numbers.Number) or
            bbox.get("south") is None or not isinstance(bbox.get("south"), numbers.Number) or
            bbox.get("east") is None or not isinstance(bbox.get("east"), numbers.Number) or
            bbox.get("west") is None or not isinstance(bbox.get("west"), numbers.Number)):
        raise AuScopeCatException(
            "Please check bbox values",
            500
        )
