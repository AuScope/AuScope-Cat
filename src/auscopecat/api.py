"""
Python library for accessing the AuScope Portal's API methods.
"""
import numbers
from types import SimpleNamespace
from requests import Response
from auscopecat.auscopecat_types import AuScopeCatException, DownloadType, \
        ServiceType, SpatialSearchType
from auscopecat.network import request


API_URL = "https://portal.auscope.org/api/"
#API_URL = "http://localhost:8080/api/"
SEARCH_URL = "searchCSWRecords.do"
SEARCH_FIELDS = [
    "fileIdentifier", "serviceName", "descriptiveKeywords",
    "dataIdentificationAbstract", "onlineResources.name",
    "onlineResources.description"
]


def search(pattern: str, ogc_types: list[ServiceType] = None,
           spatial_search_type: SpatialSearchType = None,
           bbox: dict = None, polygon: list[list[float]] = None) -> list[SimpleNamespace]:
    """
    Searches catalogue for service online resource results

    :param pattern: search for this string
    :param ogc_types: limit results to those containing one or more of the specified OGC service
        types (Optional)
    :param spatial_search_type: the type of spatial search (intersects, coontains within).
        Used with bbox (Optional)
    :param bbox: the bounding box for the search data e.g. {"north":-31.456, "east":129.653...}
    :param polygon: a list of points defined as a 2 element list of [latitude, longitude],
        e.g. [[-31.0, 125.0], [-32, 128.0], [-31.0, 128.0], [-31.0, 125.0]] (Optional)
    :return: a list of SimpleNamespace objects of the form: namespace(url, type, name)
    """
    validate_search_inputs(pattern, ogc_types, spatial_search_type, bbox, polygon)
    search_query = build_search_query(pattern, ogc_types, spatial_search_type, bbox)
    search_request = request(search_query)
    search_results = []
    if search_request.status_code == 200:
        results_json = search_request.json()
        if results_json.get("data") and results_json.get("data").get("totalCSWRecordHits") > 0:
            for result in results_json.get("data").get("cswRecords"):
                if result.get("onlineResources"):
                    for online_resource in result.get("onlineResources"):
                        if ogc_types is None or len(ogc_types) == 0 or next(\
                                (x for x in ogc_types if x.value.lower() == \
                                 online_resource.get("type").lower()), None):
                            search_results.append(SimpleNamespace(
                                   url = online_resource.get("url"),
                                   type = online_resource.get("type"),
                                   name = online_resource.get("name")
                            ))
    return search_results


def search_records(pattern: str, ogc_types: list[ServiceType] = None,
                   spatial_search_type: SpatialSearchType = None,
                   bbox: dict = None, polygon: list[list[float]] = None) -> list[SimpleNamespace]:
    """
    Searches catalogue for records

    :param pattern: search for this string
    :param ogc_type: search for a certain kind of OGC service (Optional)
    :param spatial_search_type: the type of spatial search (intersects, coontains within).
        Used with bbox (Optional)
    :param bbox: the bounding box for the search data e.g. {"north":-31.456, "east":129.653...}
    :param polygon: a list of points defined as a 2 element list of [latitude, longitude],
        e.g. [[-31.0, 125.0], [-32, 128.0], [-31.0, 128.0], [-31.0, 125.0]] (Optional)
    :return: A simpleNamespace of the form:
             namespace(
                id, name, description, record_info_url,
                constraints[], use_limit_constraints[], access_constraints[], date,
                geographic_elements[
                    namespace(type, east, west, north, south)
                ],
                online_resources[
                    namespace(url, type, name, description, version)
                ]
            )
    """
    validate_search_inputs(pattern, ogc_types, spatial_search_type, bbox, polygon)
    search_query = build_search_query(pattern, spatial_search_type=spatial_search_type, bbox=bbox)
    search_request = request(search_query)
    search_results = []
    if search_request.status_code == 200:
        results_json = search_request.json()
        if results_json.get("data") and results_json.get("data").get("totalCSWRecordHits") > 0:
            for result in results_json.get("data").get("cswRecords"):
                record = SimpleNamespace(
                    id = result.get("id", ""),
                    name = result.get("serviceName", ""),
                    description = result.get("description", ""),
                    record_info_url = result.get("recordInfoUrl", ""),
                    constraints = result.get("constraints", []),
                    use_limit_constraints = result.get("useLimitConstraints", []),
                    access_constraints = result.get("accessConstraints", []),
                    date = result.get("date", "")
                )
                geographic_elements = []
                if result.get("geographicElements") and len(result.get("geographicElements")) > 0:
                    for geog in result.get("geographicElements"):
                        geographic_elements.append(SimpleNamespace(
                            type = geog.get("type", ""),
                            east = geog.get("eastBoundLongitude", None),
                            west = geog.get("westBoundLongitude", None),
                            north = geog.get("northBoundLatitude", None),
                            south = geog.get("southBoundLatitude", None),
                        ))
                record.geographic_elements = geographic_elements
                online_resources = []
                if result.get("onlineResources"):
                    for resource in result.get("onlineResources"):
                        if ogc_types is None or len(ogc_types) == 0 or next(\
                                (x for x in ogc_types if x.value.lower() == \
                                 resource.get("type").lower()), None):
                            online_resources.append(SimpleNamespace(
                                    url = resource.get("url", ""),
                                    type = resource.get("type", ""),
                                    name = resource.get("name", ""),
                                    description = resource.get("description", ""),
                                    version = resource.get("version", "")
                            ))
                record.online_resources = online_resources
                search_results.append(record)
    return search_results


def wfs_get_feature(url: str, type_name: str, bbox: dict, version = "1.1.0",
                    srs_name: str = "EPSG:4326", output_format = "csv",
                    max_features = None) -> Response:
    """
    Make a WFS GetFeature request and return the Response object

    :param url: the WFS service URL
    :param type_name the typeName parameter of the GetFeature request
    :param bbox: the bounding box for the search data e.g. {"north":-31.456, "east":129.653...}
    :param version: version number (Optional)
    :param srs_name the SRS, e.g. "EPSG:4326" (Optional)
    :output_format: the output format (Optional)
    :max_features: maximum number of features to return (Optional)
    :return: the WFS GetFeature Response object
    """
    if bbox is None:
        raise AuScopeCatException(
            "A bounding box (bbox) must be specified",
            500
        )
    validate_bbox(bbox)

    bbox_param = f'{bbox.get("south")},{bbox.get("west")},{bbox.get("north")},{bbox.get("east")}'

    request_params = dict(
        service="wfs",
        version=version,
        request="GetFeature",
        typeNames=type_name,
        srsName=srs_name,
        bbox=bbox_param,
        outputFormat=output_format
    )

    if max_features is not None:
        request_params["maxFeatures"] = max_features

    response = request(url, request_params)
    return response


def download(obj: SimpleNamespace, download_type: DownloadType,
             bbox: dict = None, srs_name: str = "EPSG:4326",
             max_features: int = None, version: str = "1.1.0",
             file_name: str = "download.csv") -> any:
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
    validate_bbox(bbox)

    # TODO: Check to see if zip file specified, or append .zip if no extension
    if file_name and file_name == "":
        raise AuScopeCatException(
            "If file_name is specified it cannot be empty",
            500
        )

    if download_type is None:
        download_type = DownloadType.CSV

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


def validate_bbox(bbox: dict):
    """
    Validate a bounding box
    :param bbox: the bounding box, a dict with "north", "south", "east" and "west" keys
    """
    if not all(bbox.get(x) is not None and \
               isinstance(bbox.get(x), numbers.Number) \
                for x in ["north", "south", "east", "west"]):
        raise AuScopeCatException(
            "Please check bbox values",
            500
        )


def validate_polygon(polygon: list[list[float]]):
    """
    Validate a polygon
    :param the polygon as a list of points, where each point  is a 2 element list (lat, lon)
    """
    point_count = len(polygon)
    if point_count < 3:
        raise AuScopeCatException(
            "A polygon must contain at least 3 points",
            500
        )
    # If the first/last points don't match, add the first point to the end
    if polygon[0][0] != polygon[point_count - 1][0] or polygon[0][1] != polygon[point_count - 1][1]:
        polygon.append([polygon[0][0], polygon[0][1]])


def validate_search_inputs(pattern: str, ogc_types: list[ServiceType] = None,
           spatial_search_type: SpatialSearchType = None,
           bbox: dict = None, polygon: list[list[float]] = None):
    """
    Validate search inputs. Raises AuScopeCatExceptin if validation fails.
    :param pattern: search for this string
    :param ogc_types: limit results to those containing one or more of the specified OGC service
                      types (Optional)
    :param spatial_search_type: the type of spatial search (intersects, coontains within).
        Used with bbox (Optional)
    :param bbox: the bounding box for the search data e.g. {"north":-31.456, "east":129.653...}
    :param polygon: a list of points defined as a 2 element list of [latitude, longitude],
        e.g. [[-31.0, 125.0], [-32, 128.0], [-31.0, 128.0], [-31.0, 125.0]] (Optional)
    """
    if pattern is None or pattern == "":
        raise AuScopeCatException(
            "Parameter pattern can not be empty",
            500
        )
    if ogc_types is not None and len(ogc_types) > 0:
        invalid_ogc_types = []
        for ogc in ogc_types:
            if not isinstance(ogc, ServiceType):
                invalid_ogc_types.append(ogc)
        if len(invalid_ogc_types) > 0:
            raise AuScopeCatException(
                    f"Unknown service type(s): {invalid_ogc_types}",
                    500
                )
    if spatial_search_type and (bbox is None and polygon is None):
        raise AuScopeCatException(
            "Spatial search requires a bbox (bounding box) or polygon (polygon) to be specified",
            500
        )
    if spatial_search_type and (bbox or polygon):
        if not isinstance(spatial_search_type, SpatialSearchType):
            raise AuScopeCatException(
                f"Unknown spatial search type: {spatial_search_type}",
                500
            )
        if bbox:
            validate_bbox(bbox)
        if polygon:
            validate_polygon(polygon)


def build_search_query(pattern: str, ogc_types: list[ServiceType] = None,
           spatial_search_type: SpatialSearchType = None,
           bbox: dict = None, polygon: list[list[float]] = None) -> str:
    """
    :param pattern: search for this string
    :param ogc_types: limit results to those containing one or more of the specified OGC service
                      types (Optional)
    :param spatial_search_type: the type of spatial search (intersects, coontains within).
        Used with either bbox or polygon (Optional)
    :param bbox: the bounding box for the search data e.g. {"north":-31.456, "east":129.653...}
    :param polygon: a list of points defined as a 2 element list of [latitude, longitude],
        e.g. [[-31.0, 125.0], [-32, 128.0], [-31.0, 128.0], [-31.0, 125.0]] (Optional)
    :return the search query as a string
    """
    # Build search query
    search_query = f"{API_URL}{SEARCH_URL}?query={pattern}"

    # OGC services (WFS, WMS etc)
    if ogc_types is not None and len(ogc_types) > 0:
        for ogc in ogc_types:
            search_query += f"&ogcServices={ogc.value}"

    # Specify CSW fields only in order to ignore KnownLayer results
    for field in SEARCH_FIELDS:
        search_query += f"&fields={field}"

    # Spatial search if requested
    if spatial_search_type and (bbox or polygon):
        search_query += f"&spatialRelation={spatial_search_type.value}"
        if (bbox):
            search_query += f'&westBoundLongitude={bbox.get("west")}&eastBoundLongitude={bbox.get("east")}' \
                            f'&southBoundLatitude={bbox.get("south")}&northBoundLatitude={bbox.get("north")}'
        else:
            for point in polygon:
                search_query += f"&points=[{point[0]},{point[1]}]"

    return search_query
