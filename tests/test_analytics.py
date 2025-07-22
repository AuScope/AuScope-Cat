"""Tests for Google Analytics 4 integration."""
import os
import unittest
from unittest.mock import patch, MagicMock
import time

import pytest

from auscopecat.analytics import (
    GA4Analytics, 
    track_api_search, 
    track_api_download, 
    track_api_nvcl_query,
    _extract_domain
)


class TestGA4Analytics(unittest.TestCase):
    """Test GA4Analytics class functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Clear environment variables
        os.environ.pop('GA4_MEASUREMENT_ID', None)
        os.environ.pop('GA4_API_SECRET', None)
    
    def test_analytics_disabled_without_credentials(self):
        """Test analytics is disabled when credentials are missing."""
        analytics = GA4Analytics()
        assert not analytics.enabled
        assert analytics.measurement_id is None
        assert analytics.api_secret is None
    
    def test_analytics_enabled_with_credentials(self):
        """Test analytics is enabled when credentials are provided."""
        os.environ['GA4_MEASUREMENT_ID'] = 'G-TEST123'
        os.environ['GA4_API_SECRET'] = 'test-secret'
        
        analytics = GA4Analytics()
        assert analytics.enabled
        assert analytics.measurement_id == 'G-TEST123'
        assert analytics.api_secret == 'test-secret'
        assert analytics.client_id  # Should generate a UUID
    
    @patch('auscopecat.analytics.requests.post')
    def test_send_event_with_credentials(self, mock_post):
        """Test sending events when credentials are available."""
        os.environ['GA4_MEASUREMENT_ID'] = 'G-TEST123'
        os.environ['GA4_API_SECRET'] = 'test-secret'
        
        mock_post.return_value.status_code = 204
        
        analytics = GA4Analytics()
        analytics.send_event('test_event', {'param1': 'value1'})
        
        # Give thread time to execute
        time.sleep(0.1)
        
        assert mock_post.called
        call_args = mock_post.call_args
        assert call_args[1]['params']['measurement_id'] == 'G-TEST123'
        assert call_args[1]['params']['api_secret'] == 'test-secret'
        assert 'test_event' in str(call_args[1]['json'])
    
    def test_send_event_without_credentials(self):
        """Test sending events when credentials are missing."""
        analytics = GA4Analytics()
        
        # Should not raise any exceptions
        analytics.send_event('test_event', {'param1': 'value1'})
        assert not analytics.enabled
    
    @patch('auscopecat.analytics.requests.post')
    def test_send_event_handles_exceptions(self, mock_post):
        """Test that exceptions in analytics don't break functionality."""
        os.environ['GA4_MEASUREMENT_ID'] = 'G-TEST123'
        os.environ['GA4_API_SECRET'] = 'test-secret'
        
        mock_post.side_effect = Exception("Network error")
        
        analytics = GA4Analytics()
        # Should not raise any exceptions
        analytics.send_event('test_event')
        
        # Give thread time to execute and handle exception
        time.sleep(0.1)
    
    @patch('auscopecat.analytics.requests.post')
    def test_event_payload_structure(self, mock_post):
        """Test that events are sent with correct payload structure."""
        os.environ['GA4_MEASUREMENT_ID'] = 'G-TEST123'
        os.environ['GA4_API_SECRET'] = 'test-secret'
        
        mock_post.return_value.status_code = 204
        
        analytics = GA4Analytics()
        analytics.send_event('test_event', {'custom_param': 'test_value'})
        
        # Give thread time to execute
        time.sleep(0.1)
        
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        
        assert 'client_id' in payload
        assert 'events' in payload
        assert len(payload['events']) == 1
        assert payload['events'][0]['name'] == 'test_event'
        assert 'timestamp_micros' in payload['events'][0]['params']
        assert payload['events'][0]['params']['source'] == 'python_api'
        assert payload['events'][0]['params']['custom_param'] == 'test_value'


class TestTrackingFunctions(unittest.TestCase):
    """Test the tracking helper functions."""
    
    def setUp(self):
        """Set up test environment."""
        os.environ.pop('GA4_MEASUREMENT_ID', None)
        os.environ.pop('GA4_API_SECRET', None)
    
    @patch('auscopecat.analytics._analytics.send_event')
    def test_track_api_search_with_all_params(self, mock_send_event):
        """Test API search tracking with all parameters."""
        track_api_search('test pattern', ['WFS'], True)
        
        mock_send_event.assert_called_once_with('api_search', {
            'search_pattern_length': 12,
            'has_ogc_filter': True,
            'has_spatial_filter': True
        })
    
    @patch('auscopecat.analytics._analytics.send_event')
    def test_track_api_search_minimal(self, mock_send_event):
        """Test API search tracking with minimal parameters."""
        track_api_search('test')
        
        mock_send_event.assert_called_once_with('api_search', {
            'search_pattern_length': 4,
            'has_ogc_filter': False,
            'has_spatial_filter': False
        })
    
    @patch('auscopecat.analytics._analytics.send_event')
    def test_track_api_search_empty_pattern(self, mock_send_event):
        """Test API search tracking with empty pattern."""
        track_api_search('')
        
        mock_send_event.assert_called_once_with('api_search', {
            'search_pattern_length': 0,
            'has_ogc_filter': False,
            'has_spatial_filter': False
        })
    
    @patch('auscopecat.analytics._analytics.send_event')
    def test_track_api_search_none_pattern(self, mock_send_event):
        """Test API search tracking with None pattern."""
        track_api_search(None)
        
        mock_send_event.assert_called_once_with('api_search', {
            'search_pattern_length': 0,
            'has_ogc_filter': False,
            'has_spatial_filter': False
        })
    
    @patch('auscopecat.analytics._analytics.send_event')
    def test_track_api_download(self, mock_send_event):
        """Test API download tracking."""
        track_api_download('CSV', 'https://example.com/data')
        
        mock_send_event.assert_called_once_with('api_download', {
            'download_type': 'csv',
            'service_domain': 'example.com'
        })
    
    @patch('auscopecat.analytics._analytics.send_event')
    def test_track_api_download_complex_url(self, mock_send_event):
        """Test API download tracking with complex URL."""
        track_api_download('GeoJSON', 'https://subdomain.example.com:8080/wfs?service=WFS&version=1.1.0')
        
        mock_send_event.assert_called_once_with('api_download', {
            'download_type': 'geojson',
            'service_domain': 'subdomain.example.com:8080'
        })
    
    @patch('auscopecat.analytics._analytics.send_event')
    def test_track_api_download_none_type(self, mock_send_event):
        """Test API download tracking with None download type."""
        track_api_download(None, 'https://example.com/data')
        
        mock_send_event.assert_called_once_with('api_download', {
            'download_type': 'unknown',
            'service_domain': 'example.com'
        })
    
    @patch('auscopecat.analytics._analytics.send_event')
    def test_track_api_nvcl_query_search(self, mock_send_event):
        """Test NVCL search query tracking."""
        track_api_nvcl_query('search_tsg')
        
        mock_send_event.assert_called_once_with('api_nvcl_query', {
            'nvcl_query_type': 'search_tsg'
        })
    
    @patch('auscopecat.analytics._analytics.send_event')
    def test_track_api_nvcl_query_download(self, mock_send_event):
        """Test NVCL download query tracking."""
        track_api_nvcl_query('download_tsg')
        
        mock_send_event.assert_called_once_with('api_nvcl_query', {
            'nvcl_query_type': 'download_tsg'
        })


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_extract_domain_simple(self):
        """Test domain extraction from simple URLs."""
        assert _extract_domain('https://example.com/path') == 'example.com'
        assert _extract_domain('http://example.com/path') == 'example.com'
    
    def test_extract_domain_with_port(self):
        """Test domain extraction from URLs with ports."""
        assert _extract_domain('http://subdomain.example.com:8080/path') == 'subdomain.example.com:8080'
        assert _extract_domain('https://localhost:3000/api') == 'localhost:3000'
    
    def test_extract_domain_complex(self):
        """Test domain extraction from complex URLs."""
        assert _extract_domain('https://portal.auscope.org.au/api/search?query=test') == 'portal.auscope.org.au'
        assert _extract_domain('ftp://ftp.example.com/files/data.zip') == 'ftp.example.com'
    
    def test_extract_domain_invalid_urls(self):
        """Test domain extraction from invalid URLs."""
        assert _extract_domain('invalid-url') == ''  # urlparse returns empty netloc for invalid URLs
        assert _extract_domain('') == ''
        assert _extract_domain('not-a-url-at-all') == ''
    
    def test_extract_domain_edge_cases(self):
        """Test domain extraction edge cases."""
        assert _extract_domain('http://') == ''
        assert _extract_domain('https://example.com') == 'example.com'
        assert _extract_domain('//example.com/path') == 'example.com'


class TestIntegrationWithRealAPI(unittest.TestCase):
    """Integration tests with real API calls (requires credentials)."""
    
    def setUp(self):
        """Set up test environment."""
        self.has_credentials = bool(
            os.getenv('GA4_MEASUREMENT_ID') and os.getenv('GA4_API_SECRET')
        )
    
    @unittest.skipUnless(
        os.getenv('GA4_MEASUREMENT_ID') and os.getenv('GA4_API_SECRET'),
        "GA4 credentials not available"
    )
    def test_end_to_end_analytics(self):
        """Test end-to-end analytics with real GA4 credentials."""
        from auscopecat.api import search
        from auscopecat.auscopecat_types import ServiceType
        
        # This should trigger analytics tracking
        results = search('borehole', [ServiceType.WFS])
        
        # Verify search worked
        assert isinstance(results, list)
        # Analytics should be triggered in background - no way to verify without GA4 access
        
        # Give analytics time to send
        time.sleep(1)
    
    def test_analytics_graceful_failure_without_credentials(self):
        """Test that analytics fails gracefully without credentials."""
        # Clear any existing credentials
        old_measurement_id = os.environ.pop('GA4_MEASUREMENT_ID', None)
        old_api_secret = os.environ.pop('GA4_API_SECRET', None)
        
        try:
            from auscopecat.api import search
            from auscopecat.auscopecat_types import ServiceType
            
            # This should work even without analytics credentials
            results = search('borehole', [ServiceType.WFS])
            assert isinstance(results, list)
            
        finally:
            # Restore credentials if they existed
            if old_measurement_id:
                os.environ['GA4_MEASUREMENT_ID'] = old_measurement_id
            if old_api_secret:
                os.environ['GA4_API_SECRET'] = old_api_secret


if __name__ == '__main__':
    unittest.main() 