from enum import Enum

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

class AuScopeCatException(Exception):
    def __init__(self, message, error_code):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
