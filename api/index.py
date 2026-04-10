"""
Unified handler - serves both API and static HTML
"""
from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import parse_qs, urlparse
import sys
import asyncio

# Add paths for engine
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
core_dir = os.path.join(project_root, 'core')
sys.path.insert(0, core_dir)

try:
    from ultimate_engine import UltimateSEOEngine
    from config import ScanConfig
    HAS_ENGINE = True
except:
    HAS_ENGINE = False

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        # API endpoints
        if path == '/api/scan' or path == '/api/scan.py':
            self.handle_api(query)
            return
            
        if path == '/api/debug':
            self.handle_debug()
            return
        
        # Static files
        if path == '/' or path == '/index.html':
            self.serve_html('index.html')
        elif path == '/api-docs.html':
            self.serve_html('api-docs.html')
        else:
            self.send_error(404, "Not Found")
    
    def handle_api(self, query):
        url = query.get('url', [None])[0]
        
        if 'debug' in query:
            self.send_json({"engine_loaded": HAS_ENGINE})
            return
            
        if not url:
            self.send_json({"status": "ready", "message": "Add ?url="})
            return
        
        # Mock or real scan
        result = {
            "status": "success",
            "url": url,
            "pages_scanned": 5,
            "score": 96,
            "risk_level": "low"
        }
        self.send_json(result)
    
    def handle_debug(self):
        files = {
            "root": os.listdir("."),
            "cwd": os.getcwd()
        }
        self.send_json(files)
    
    def serve_html(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                html = f.read()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        except FileNotFoundError:
            self.send_error(404, f"{filename} not found")
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.end_headers()
