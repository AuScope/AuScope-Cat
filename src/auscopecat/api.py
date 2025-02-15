import numbers
import urllib
from auscopecat.auscopecat_types import AuScopeCatException, DownloadType, ServiceType, SpatialSearchType
from auscopecat.network import request
from types import SimpleNamespace


API_URL = "https://auportal-dev.geoanalytics.group/api/"
#API_URL = "http://localhost:8080/api/"
DOWNLOAD_URL = "getAllFeaturesInCSV.do"
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
    except Exception as e:
        raise AuScopeCatException(
            f"Error querying data: {e}",
            500
        )

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


def download(obj: SimpleNamespace, download_type: DownloadType, bbox: dict = None, file_name: str = None) -> any:
    """
    Downloads data from object

    :param obj: SimpleNamespace objects with "url", "type" and "name" attributes
    :param download_type: type of download
    :param bbox: the bounding box for the download data e.g. {"north":-31.456, "east":129.653...}
    :param file_name: the file name for the download (Optional)
    :return: CSV data
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

    # TODO: Supply CRS?
    bbox_param = (f'{{"crs":"EPSG:4326",'
                  f'"eastBoundLongitude":{bbox.get("east")},'
                  f'"westBoundLongitude":{bbox.get("west")},'
                  f'"northBoundLatitude":{bbox.get("north")},"southBoundLatitude":{bbox.get("south")}}}')

    # URL, name and bbox will need to be double encoded
    feature_download_url = urllib.parse.quote_plus(obj.url) + \
                           "&typeName=" + urllib.parse.quote_plus(obj.name) + \
                           "&bbox=" + urllib.parse.quote_plus(bbox_param)
    feature_download_url = urllib.parse.quote_plus(feature_download_url)
    service_url = f"{API_URL}{DOWNLOAD_URL}?serviceUrl={feature_download_url}"
    download_url = f"{API_URL}downloadGMLAsZip.do?outputFormat={download_type.value}&serviceUrls={service_url}"

    try:
        response = request(download_url)
        if response and response.status_code and response.status_code == 200:
            f_name = "download.zip" if not file_name else file_name
            with open(f_name, "wb") as f:
                f.write(response.content)
        else:
            raise AuScopeCatException(
                f"Invalid response ({response.status_code}): {response.reason}",
                500
            )
    except Exception as e:
        raise AuScopeCatException(
            "Error downloading data",
            500
        )


def validate_bbox(bbox: dict):
    if (bbox.get("north") is None or not isinstance(bbox.get("north"), numbers.Number) or
            bbox.get("south") is None or not isinstance(bbox.get("south"), numbers.Number) or
            bbox.get("east") is None or not isinstance(bbox.get("east"), numbers.Number) or
            bbox.get("west") is None or not isinstance(bbox.get("west"), numbers.Number)):
        raise AuScopeCatException(
            "Please check bbox values",
            500
        )
