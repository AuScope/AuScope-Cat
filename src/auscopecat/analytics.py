"""
Google Analytics 4 Measurement Protocol integration for tracking API usage.
"""
import logging
import os
import threading
import time
import uuid
from typing import Optional

import requests


LOGGER = logging.getLogger(__name__)


class GA4Analytics:
    """Google Analytics 4 Measurement Protocol client for tracking API usage."""
    
    def __init__(self):
        """Initialize GA4 Analytics with environment variables."""
        self.measurement_id = os.getenv('GA4_MEASUREMENT_ID')
        self.api_secret = os.getenv('GA4_API_SECRET')
        
        # Use consistent client ID for better tracking
        # In production, this creates a stable anonymous identifier
        # For debugging, can be overridden with GA4_DEBUG_CLIENT_ID
        debug_client_id = os.getenv('GA4_DEBUG_CLIENT_ID')
        if debug_client_id:
            self.client_id = debug_client_id
        else:
            # Create stable client ID based on hostname for consistent tracking
            import socket
            hostname = socket.gethostname()
            self.client_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, hostname))
        
        self.enabled = bool(self.measurement_id and self.api_secret)
        
        if not self.enabled:
            LOGGER.debug("GA4 analytics disabled - missing credentials")
    
    def send_event(self, event_name: str, parameters: Optional[dict] = None) -> None:
        """
        Send an event to Google Analytics 4 via Measurement Protocol.
        
        :param event_name: Name of the event (e.g., 'api_search', 'api_download')
        :param parameters: Additional event parameters
        """
        if not self.enabled:
            return
            
        # Run analytics in background thread to avoid blocking API calls
        thread = threading.Thread(
            target=self._send_event_async,
            args=(event_name, parameters or {}),
            daemon=True
        )
        thread.start()
    
    def _send_event_async(self, event_name: str, parameters: dict) -> None:
        """Send event asynchronously to avoid blocking main API calls."""
        try:
            url = f"https://www.google-analytics.com/mp/collect"
            
            payload = {
                "client_id": self.client_id,
                "events": [{
                    "name": event_name,
                    "params": {
                        "timestamp_micros": int(time.time() * 1_000_000),
                        "source": "python_api",
                        "api_version": "1.0.1",  # Match package version
                        **parameters
                    }
                }]
            }
            
            params = {
                "measurement_id": self.measurement_id,
                "api_secret": self.api_secret
            }
            
            # Send with short timeout to avoid hanging
            response = requests.post(
                url,
                params=params,
                json=payload,
                timeout=5
            )
            
            if response.status_code != 204:
                LOGGER.debug(f"GA4 event failed: {response.status_code}")
                
        except Exception as e:
            # Analytics should never break the main API functionality
            LOGGER.debug(f"GA4 analytics error: {e}")


# Global analytics instance
_analytics = GA4Analytics()


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