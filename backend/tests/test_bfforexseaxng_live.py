#!/usr/bin/env python3
"""
Live integration test for bfforexseaXNG service
Tests the actual connection to http://localhost:8081
"""

import asyncio
import aiohttp
import sys
import os
sys.path.append('..')

from services.web_search_service import WebSearchService

async def test_bfforexseaxng_live():
    """Test live bfforexseaXNG service"""
    print("🔍 Testing live bfforexseaXNG integration at http://localhost:8081")
    print("=" * 60)
    
    # Configure service for bfforexseaXNG
    config = {
        'default_engine': 'bfforexseaxng',
        'engines': {
            'bfforexseaxng': {
                'enabled': True,
                'instance_url': 'http://localhost:8081'
            }
        }
    }
    
    service = WebSearchService(config)
    
    # Test 1: Service Status
    print("📊 Test 1: Service Status")
    status = service.get_service_status()
    bfforex_status = status['engines'].get('bfforexseaxng', {})
    print(f"   Available: {bfforex_status.get('available', False)}")
    print(f"   Configured: {bfforex_status.get('configured', False)}")
    print(f"   Description: {bfforex_status.get('description', 'N/A')}")
    print()
    
    # Test 2: Check if service is reachable
    print("🌐 Test 2: Service Connectivity")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8081', timeout=5) as response:
                print(f"   Status Code: {response.status}")
                if response.status == 200:
                    print("   ✅ bfforexseaXNG service is running!")
                else:
                    print(f"   ⚠️  Service responded with status {response.status}")
    except aiohttp.ClientConnectorError:
        print("   ❌ Cannot connect to bfforexseaXNG service at localhost:8081")
        print("   💡 Make sure the service is running with: docker run -p 8081:8080 searxng/searxng")
        return False
    except asyncio.TimeoutError:
        print("   ❌ Connection timeout to bfforexseaXNG service")
        return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False
    print()
    
    # Test 3: Search Functionality
    print("🔎 Test 3: Search Functionality")
    test_queries = [
        "Python programming tutorial",
        "machine learning basics",
        "cryptocurrency news"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"   Query {i}: '{query}'")
        try:
            result = await service.search_web(query, max_results=3, engine='bfforexseaxng')
            
            if result['success']:
                print(f"   ✅ Found {len(result['results'])} results")
                for j, res in enumerate(result['results'], 1):
                    title = res['title'][:50] + "..." if len(res['title']) > 50 else res['title']
                    print(f"      {j}. {title}")
            else:
                print(f"   ❌ Search failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   ❌ Search error: {e}")
        print()
    
    # Test 4: Auto Search Detection
    print("🤖 Test 4: Auto Search Detection")
    auto_queries = [
        "search for latest AI news",
        "what is blockchain technology", 
        "Hello, how are you?"  # Should not trigger search
    ]
    
    for query in auto_queries:
        print(f"   Query: '{query}'")
        try:
            result = await service.auto_search(query)
            if result is None:
                print("   ➡️  No search triggered (as expected)")
            elif result['success']:
                print(f"   ✅ Auto search triggered, found {len(result['results'])} results")
                print(f"   📊 Confidence: {result['search_intent']['confidence']:.2f}")
            else:
                print(f"   ❌ Auto search failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   ❌ Auto search error: {e}")
        print()
    
    # Test 5: Rate Limiting
    print("⏱️  Test 5: Rate Limiting")
    try:
        start_time = asyncio.get_event_loop().time()
        
        # Make two quick requests
        await service.search_web("rate limit test 1", max_results=1, engine='bfforexseaxng')
        await service.search_web("rate limit test 2", max_results=1, engine='bfforexseaxng')
        
        end_time = asyncio.get_event_loop().time()
        elapsed = end_time - start_time
        
        print(f"   Time for 2 requests: {elapsed:.2f} seconds")
        if elapsed >= service.min_request_interval:
            print("   ✅ Rate limiting is working correctly")
        else:
            print("   ⚠️  Rate limiting may not be enforced")
    except Exception as e:
        print(f"   ❌ Rate limiting test error: {e}")
    print()
    
    print("🎉 Live integration test completed!")
    return True

async def test_search_quality():
    """Test search result quality and ranking"""
    print("\n📈 Testing Search Quality & Ranking")
    print("=" * 40)
    
    config = {
        'engines': {
            'bfforexseaxng': {
                'enabled': True,
                'instance_url': 'http://localhost:8081'
            }
        }
    }
    
    service = WebSearchService(config)
    
    # Test quality scoring
    test_query = "Python web development frameworks"
    
    try:
        result = await service.search_web(test_query, max_results=5, engine='bfforexseaxng')
        
        if result['success'] and result['results']:
            print(f"Search results for: '{test_query}'")
            print("-" * 50)
            
            for i, res in enumerate(result['results'], 1):
                quality_score = res.get('quality_score', 0)
                title = res['title'][:60] + "..." if len(res['title']) > 60 else res['title']
                url = res['url'][:50] + "..." if len(res['url']) > 50 else res['url']
                
                print(f"{i}. Quality: {quality_score:.3f}")
                print(f"   Title: {title}")
                print(f"   URL: {url}")
                print(f"   Snippet: {res['snippet'][:100]}...")
                print()
            
            # Check if results are properly sorted by quality
            scores = [res.get('quality_score', 0) for res in result['results']]
            is_sorted = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
            
            if is_sorted:
                print("✅ Results are properly sorted by quality score")
            else:
                print("⚠️  Results may not be optimally sorted")
                
            print(f"📊 Total found: {result.get('total_found', 'N/A')}")
            print(f"📊 After deduplication: {result.get('after_deduplication', 'N/A')}")
            
        else:
            print(f"❌ Quality test failed: {result.get('error', 'No results')}")
            
    except Exception as e:
        print(f"❌ Quality test error: {e}")

if __name__ == "__main__":
    print("🚀 Starting bfforexseaXNG Live Integration Tests")
    print("=" * 60)
    
    try:
        # Run connectivity and basic functionality tests
        success = asyncio.run(test_bfforexseaxng_live())
        
        if success:
            # Run quality tests if basic tests pass
            asyncio.run(test_search_quality())
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
    
    print("\n" + "=" * 60)
    print("Tests completed. Check output above for results.")