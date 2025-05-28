"""
Util functions for the AuScopeCat library
"""
import numbers

import requests

from auscopecat.auscopecat_types import AuScopeCatError, BoundingBox


def validate_bbox(bbox: dict, adjust_bounds = False) -> BoundingBox:
    """
    Validate a bounding box
    :param bbox: the bounding box, a dict with "north", "south", "east" and
        "west" keys
    :param adjust_bounds: if True, and the bounds are outside of the allowable
        range (i.e. north > 90.0, south < -90.0, east > 180.0 and west <
        -180.0) then an Exception will not be thrown but instead the values
        will be corrected to the closest lowest/highest value for that
        coordinate
    :return the validated bounding box provided no AuScopeCatError is
        thrown
    """
    if not all(bbox.get(x) is not None and \
               isinstance(bbox.get(x), numbers.Number) \
                for x in ["north", "south", "east", "west"]):
        raise AuScopeCatError(
            "Please check bbox values",
            500
        )
    if bbox.get("north") > 90.0:
        if adjust_bounds:
            bbox["north"] = 90.0
        else:
            raise AuScopeCatError(
                "bbox['north'] cannot exceed 90.0",
                500
            )
    if bbox.get("south") < -90.0:
        if adjust_bounds:
            bbox["south"] = -90.0
        else:
            raise AuScopeCatError(
                "bbox['south'] cannot be less than -90.0",
                500
            )
    if bbox.get("west") < -180.0:
        if adjust_bounds:
            bbox["west"] = -180.0
        else:
            raise AuScopeCatError(
                "bbox['west'] cannot be less than -180.0",
                500
            )
    if bbox.get("east") > 180.0:
        if adjust_bounds:
            bbox["east"] = 180.0
        else:
            raise AuScopeCatError(
                "bbox['east'] cannot exceed 180.0",
                500
            )
    return bbox


def validate_polygon(polygon: list[list[float]]):
    """
    Validate a polygon
    :param the polygon as a list of points, where each point  is a 2 element list (lat, lon)
    """
    point_count = len(polygon)
    if point_count < 3:
        raise AuScopeCatError(
            "A polygon must contain at least 3 points",
            500
        )
    # If the first/last points don't match, add the first point to the end
    if polygon[0][0] != polygon[point_count - 1][0] or polygon[0][1] != polygon[point_count - 1][1]:
        polygon.append([polygon[0][0], polygon[0][1]])

def download_url(url: str, save_path: str, chunk_size=1024*64):
    '''
    Download a file from url

    :param url: url
    :param save_path: save_path
    :param chunk_size: chunk_size (Optional)
    '''
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)
