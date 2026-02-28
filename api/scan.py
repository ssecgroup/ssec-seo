"""
ssec-seo API for Vercel - FINAL WORKING VERSION
"""
import sys
import os
import json
import asyncio
import traceback
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'core'))

# Direct imports (now that paths are correct)
try:
    from ultimate_engine import UltimateSEOEngine
    from config import ScanConfig
    HAS_REAL_ENGINE = True
    print(" REAL ENGINE LOADED")
except Exception as e:
    HAS_REAL_ENGINE = False
    print(f" Engine load failed: {e}")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        url = query.get('url', [None])[0]
        
        if not HAS_REAL_ENGINE:
            self.wfile.write(json.dumps({
                'status': 'error',
                'error': 'Engine not loaded',
                'mock': self.generate_mock_data(url or 'no-url')
            }).encode())
            return
        
        if not url:
            self.wfile.write(json.dumps({
                'status': 'ok',
                'message': 'ssec-seo real engine ready'
            }).encode())
            return
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            config = ScanConfig(max_pages=2, concurrent_requests=1)
            engine = UltimateSEOEngine(config)
            results = loop.run_until_complete(engine.scan(url))
            loop.close()
            
            self.wfile.write(json.dumps({
                'status': 'success',
                'url': url,
                'pages': results['statistics']['pages_crawled'],
                'issues': results['statistics']['total_issues'],
                'critical': results['statistics']['critical_issues']
            }).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps({
                'error': str(e),
                'mock': self.generate_mock_data(url)
            }).encode())
    
    def generate_mock_data(self, url):
        import random
        return {
            'url': url,
            'pages': random.randint(5, 20),
            'issues': random.randint(5, 30),
            'critical': random.randint(0, 3)
        }
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.end_headers()