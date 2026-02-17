"""
RudderStack analytics integration for tracking API usage.
"""
import atexit
import logging
import os
import socket
import uuid
from typing import Optional

import rudderstack.analytics as rudder_analytics


LOGGER = logging.getLogger(__name__)

# Default RudderStack credentials (can be overridden with environment variables)
DEFAULT_RUDDERSTACK_WRITE_KEY = "38s1jj9jSa5kz5UaTzQ8qruE4U8"
DEFAULT_RUDDERSTACK_DATA_PLANE_URL = "https://csirobenyzumqe.dataplane.rudderstack.com"

# Get package version dynamically
try:
    from importlib.metadata import version
    __version__ = version("auscopecat")
except Exception:
    __version__ = "unknown"


class RudderStackAnalytics:
    """RudderStack analytics client for tracking API usage."""

    def __init__(self):
        """Initialize RudderStack with environment variables or hardcoded defaults."""
        # Check environment variables first, fall back to hardcoded defaults
        self.write_key = os.getenv('RUDDERSTACK_WRITE_KEY', DEFAULT_RUDDERSTACK_WRITE_KEY)
        self.data_plane_url = os.getenv('RUDDERSTACK_DATA_PLANE_URL', DEFAULT_RUDDERSTACK_DATA_PLANE_URL)

        # Generate user_id using same logic as former GA4 client_id
        # Creates a stable anonymous identifier based on hostname
        # Can be overridden with RUDDERSTACK_DEBUG_USER_ID for testing
        debug_user_id = os.getenv('RUDDERSTACK_DEBUG_USER_ID')
        if debug_user_id:
            self.user_id = debug_user_id
        else:
            hostname = socket.gethostname()
            self.user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, hostname))

        self.enabled = bool(self.write_key and self.data_plane_url)

        if self.enabled:
            # Configure RudderStack SDK
            rudder_analytics.write_key = self.write_key
            rudder_analytics.dataPlaneUrl = self.data_plane_url
            rudder_analytics.gzip = True  # Enable compression

            if os.getenv('RUDDERSTACK_DEBUG'):
                rudder_analytics.debug = True

            # Register cleanup on exit to ensure events are flushed
            atexit.register(rudder_analytics.shutdown)

            LOGGER.debug("RudderStack analytics enabled")
        else:
            LOGGER.debug("RudderStack analytics disabled - missing credentials")

    def send_event(self, event_name: str, parameters: Optional[dict] = None) -> None:
        """
        Send event to RudderStack.

        :param event_name: Name of the event (e.g., 'api_search')
        :param parameters: Additional event parameters
        """
        if not self.enabled:
            return

        try:
            rudder_analytics.track(
                user_id=self.user_id,
                event=event_name,
                properties={
                    "source": "python_api",
                    "api_version": __version__,
                    **(parameters or {})
                }
            )
        except Exception as e:
            LOGGER.debug(f"RudderStack analytics error: {e}")


_analytics = RudderStackAnalytics()


def track_api_search(pattern: str, ogc_types: Optional[list] = None, 
                    spatial_search: bool = False) -> None:
    """Track API search usage."""
    parameters = {
        "search_pattern_length": len(pattern) if pattern else 0,
        "has_ogc_filter": bool(ogc_types),
        "has_spatial_filter": spatial_search
    }
    _analytics.send_event("api_search", parameters)


def track_api_download(download_type: str, url: str) -> None:
    """Track API download usage."""
    parameters = {
        "download_type": download_type.lower() if download_type else "unknown",
        "service_domain": _extract_domain(url)
    }
    _analytics.send_event("api_download", parameters)


def track_api_nvcl_query(query_type: str) -> None:
    """Track NVCL-specific API usage."""
    parameters = {
        "nvcl_query_type": query_type
    }
    _analytics.send_event("api_nvcl_query", parameters)


def _extract_domain(url: str) -> str:
    """Extract domain from URL for analytics without exposing full URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return "unknown"