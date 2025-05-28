from enum import Enum
from typing import TypedDict


class ServiceType(Enum):
    WMS = "wms"
    WFS = "wfs"
    WCS = "wcs"
    KML = "kml"

class SpatialSearchType(Enum):
    INTERSECTS = "intersects"
    CONTAINS = "contains"
    WITHIN = "within"

class DownloadType(Enum):
    CSV = "csv"

class AuScopeCatError(Exception):
    def __init__(self, message, error_code):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class BoundingBox(TypedDict):
    north: float
    east: float
    south: float
    west: float
