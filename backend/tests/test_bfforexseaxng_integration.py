import pytest
import asyncio
import aiohttp
from unittest.mock import patch, AsyncMock
import sys
sys.path.append('..')

from services.web_search_service import WebSearchService

class TestBfforexSearXNGIntegration:
    """Test suite specifically for bfforexseaXNG integration"""
    
    def setup_method(self):
        """Set up test environment"""
        self.config = {
            'default_engine': 'bfforexseaxng',
            'engines': {
                'bfforexseaxng': {
                    'enabled': True,
                    'instance_url': 'http://localhost:8081'
                }
            }
        }
        self.service = WebSearchService(self.config)
    
    def test_bfforexseaxng_configuration(self):
        """Test bfforexseaXNG is properly configured"""
        config = self.service._get_search_config('bfforexseaxng')
        
        assert config['enabled'] is True
        assert config['requires_api_key'] is False
        assert config['instance_url'] == 'http://localhost:8081'
        assert config['rate_limit'] == 1.0
        assert 'Local bfforex SearXNG instance' in config['description']
    
    def test_bfforexseaxng_is_configured(self):
        """Test bfforexseaXNG configuration checking"""
        config = {'enabled': True, 'instance_url': 'http://localhost:8081'}
        assert self.service._is_engine_configured('bfforexseaxng', config) is True
        
        # Test with missing URL
        config_no_url = {'enabled': True, 'instance_url': ''}
        assert self.service._is_engine_configured('bfforexseaxng', config_no_url) is False
        
        # Test when disabled
        config_disabled = {'enabled': False, 'instance_url': 'http://localhost:8081'}
        assert self.service._is_engine_configured('bfforexseaxng', config_disabled) is False
    
    def test_bfforexseaxng_in_supported_engines(self):
        """Test bfforexseaXNG appears in supported engines list"""
        engines = self.service.get_supported_engines()
        
        bfforex_engine = next((e for e in engines if e['name'] == 'bfforexseaxng'), None)
        assert bfforex_engine is not None
        assert bfforex_engine['display_name'] == 'bfforex SearXNG'
        assert bfforex_engine['requires_api_key'] is False
        assert bfforex_engine['requires_instance_url'] is False  # Pre-configured
        assert bfforex_engine['free'] is True
        assert 'localhost:8081' in bfforex_engine['description']
    
    def test_bfforexseaxng_in_service_status(self):
        """Test bfforexseaXNG appears in service status"""
        status = self.service.get_service_status()
        
        assert 'bfforexseaxng' in status['engines']
        bfforex_status = status['engines']['bfforexseaxng']
        assert bfforex_status['available'] is True
        assert bfforex_status['requires_api_key'] is False
        assert bfforex_status['configured'] is True
        assert 'web_search' in bfforex_status['features']
        assert 'Local bfforex SearXNG instance' in bfforex_status['description']
    
    @pytest.mark.asyncio
    async def test_bfforexseaxng_search_success(self):
        """Test successful bfforexseaXNG search"""
        mock_response_data = {
            'results': [
                {
                    'title': 'bfforex SearXNG Result 1',
                    'url': 'https://example.com/bfforex1',
                    'content': 'bfforex search result snippet 1'
                },
                {
                    'title': 'bfforex SearXNG Result 2',
                    'url': 'https://example.com/bfforex2',
                    'content': 'bfforex search result snippet 2'
                }
            ]
        }
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await self.service.search_web("test query", engine='bfforexseaxng')
            
            assert result['success'] is True
            assert result['source'] == 'bfforexseaxng'
            assert len(result['results']) == 2
            assert result['results'][0]['title'] == 'bfforex SearXNG Result 1'
            assert result['results'][0]['url'] == 'https://example.com/bfforex1'
            assert result['results'][0]['snippet'] == 'bfforex search result snippet 1'
            
            # Verify the correct URL was called
            call_args = mock_get.call_args
            assert 'http://localhost:8081/search' in str(call_args)
    
    @pytest.mark.asyncio
    async def test_bfforexseaxng_search_failure(self):
        """Test bfforexseaXNG search when service is unavailable"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 503  # Service unavailable
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await self.service.search_web("test query", engine='bfforexseaxng')
            
            assert result['success'] is False
            assert "request failed" in result['error']
            assert result['source'] == 'bfforexseaxng'
    
    @pytest.mark.asyncio 
    async def test_bfforexseaxng_connection_timeout(self):
        """Test bfforexseaXNG search with connection timeout"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = asyncio.TimeoutError("Connection timeout")
            
            result = await self.service.search_web("test query", engine='bfforexseaxng')
            
            assert result['success'] is False
            assert "timeout" in result['error'].lower() or "connection" in result['error'].lower()
    
    @pytest.mark.asyncio
    async def test_auto_search_with_bfforexseaxng(self):
        """Test auto search using bfforexseaXNG as default engine"""
        mock_response_data = {
            'results': [
                {
                    'title': 'Auto Search via bfforex',
                    'url': 'https://example.com/auto',
                    'content': 'Auto search result from bfforex SearXNG'
                }
            ]
        }
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await self.service.auto_search("search for latest Python news")
            
            assert result is not None
            assert result['success'] is True
            assert result['source'] == 'bfforexseaxng'
            assert result['auto_search'] is True
            assert 'search_intent' in result
    
    def test_bfforexseaxng_default_engine(self):
        """Test bfforexseaXNG can be set as default engine"""
        service = WebSearchService({'default_engine': 'bfforexseaxng'})
        
        # Should use bfforexseaXNG when no engine specified
        config = service._get_search_config()
        assert config['instance_url'] == 'http://localhost:8081'
        
    @pytest.mark.asyncio
    async def test_bfforexseaxng_rate_limiting(self):
        """Test rate limiting for bfforexseaXNG"""
        # Set short rate limit for testing
        self.service.min_request_interval = 0.1
        
        mock_response_data = {'results': []}
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # First request
            start_time = asyncio.get_event_loop().time()
            await self.service.search_web("first query", engine='bfforexseaxng')
            
            # Second request should be rate limited
            await self.service.search_web("second query", engine='bfforexseaxng')
            end_time = asyncio.get_event_loop().time()
            
            # Should have been delayed by rate limiting
            assert (end_time - start_time) >= 0.05  # Some buffer for timing variations

if __name__ == "__main__":
    pytest.main([__file__])