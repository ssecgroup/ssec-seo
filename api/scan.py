from http.server import BaseHTTPRequestHandler
import json
import sys
import os
from urllib.parse import parse_qs, urlparse

# Add the current directory to path so it can find spyglass module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from spyglass.core.ultimate_engine import UltimateSEOEngine
    from spyglass.core.config import ScanConfig
except ImportError as e:
    print(f"Import Error: {e}")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        try:
            # Parse query parameters
            query = parse_qs(urlparse(self.path).query)
            url = query.get('url', [''])[0]
            
            if not url:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': 'Missing url parameter'
                }).encode())
                return
            
            # Simple test response first (to verify function works)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'url': url,
                'message': 'API is working! Full scan coming soon.'
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': str(e)
            }).encode())
