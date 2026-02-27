"""
SPYGLASS API for Vercel - Direct import fix
"""
import sys
import os
import json
import asyncio
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Get the absolute path to the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add all necessary paths
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'core'))
sys.path.insert(0, os.path.join(project_root, 'core', 'crawler'))
sys.path.insert(0, os.path.join(project_root, 'core', 'scanners'))
sys.path.insert(0, os.path.join(project_root, 'core', 'reporters'))

# Direct imports from core
try:
    # Import directly from the core module
    from core.ultimate_engine import UltimateSEOEngine
    from core.config import ScanConfig
    HAS_SPYGLASS = True
    print("✅ Direct import from core succeeded")
except ImportError as e:
    try:
        # Alternative: import from the file directly
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "ultimate_engine", 
            os.path.join(project_root, "core", "ultimate_engine.py")
        )
        ultimate_engine = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ultimate_engine)
        UltimateSEOEngine = ultimate_engine.UltimateSEOEngine
        
        spec2 = importlib.util.spec_from_file_location(
            "config", 
            os.path.join(project_root, "core", "config.py")
        )
        config = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(config)
        ScanConfig = config.ScanConfig
        
        HAS_SPYGLASS = True
        print("✅ Dynamic import succeeded")
    except Exception as e2:
        HAS_SPYGLASS = False
        print(f"❌ All imports failed: {e2}")
        print(f"❌ Dynamic import failed: {e2}")

class handler(BaseHTTPRequestHandler):
    """Handle HTTP requests to Vercel"""
    
    def do_GET(self):
        """Handle GET requests"""
        self._handle_request('GET')
    
    def do_POST(self):
        """Handle POST requests"""
        self._handle_request('POST')
    
    def do_OPTIONS(self):
        """Handle CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _handle_request(self, method):
        """Handle requests"""
        
        # Parse URL
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        if not HAS_SPYGLASS:
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'error',
                'error': 'Spyglass modules could not be imported',
                'project_root': project_root,
                'core_exists': os.path.exists(os.path.join(project_root, 'core')),
                'ultimate_engine_exists': os.path.exists(os.path.join(project_root, 'core', 'ultimate_engine.py'))
            }).encode())
            return
        
        # Handle GET with URL parameter
        if method == 'GET' and 'url' in query:
            url = query['url'][0]
            
            try:
                # Run async scan
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Create minimal config
                config = ScanConfig(max_pages=1, concurrent_requests=1)
                engine = UltimateSEOEngine(config)
                
                # Run scan
                results = loop.run_until_complete(engine.scan(url))
                loop.close()
                
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'status': 'success',
                    'url': url,
                    'pages_scanned': results['statistics']['pages_crawled'],
                    'issues_found': results['statistics']['total_issues']
                }).encode())
                
            except Exception as e:
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'status': 'error',
                    'error': str(e)
                }).encode())
        
        # Handle POST for full report
        elif method == 'POST':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode())
                url = data.get('url')
                
                if not url:
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Missing url'}).encode())
                    return
                
                # Run full scan
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                config = ScanConfig(max_pages=5, concurrent_requests=2)
                engine = UltimateSEOEngine(config)
                results = loop.run_until_complete(engine.scan(url))
                
                # Generate HTML report
                report_html = engine.generate_report('html')
                loop.close()
                
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(report_html.encode())
                
            except Exception as e:
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        
        # Default response
        else:
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'ok',
                'message': 'SPYGLASS API is running',
                'endpoints': {
                    'GET /api/scan?url=example.com': 'Quick scan',
                    'POST /api/scan with {"url": "example.com"}': 'Full HTML report'
                }
            }).encode())
