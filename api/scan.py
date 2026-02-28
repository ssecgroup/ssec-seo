"""
ssec-seo API for Vercel - COMPLETE WORKING VERSION
Returns full SEO data matching frontend expectations
"""
import sys
import os
import json
import asyncio
import traceback
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Add paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
core_dir = os.path.join(project_root, 'core')
sys.path.insert(0, core_dir)

# Import the REAL engine
try:
    from ultimate_engine import UltimateSEOEngine
    from config import ScanConfig
    HAS_ENGINE = True
    print("✅ REAL SEO ENGINE LOADED")
except Exception as e:
    print(f"❌ Failed: {e}")
    HAS_ENGINE = False

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests - Quick scan"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        url = query.get('url', [None])[0]
        
        # Debug endpoint
        if 'debug' in query:
            debug_info = {
                'engine_loaded': HAS_ENGINE,
                'core_exists': os.path.exists(core_dir),
                'python_path': sys.path[:3]
            }
            self.wfile.write(json.dumps(debug_info).encode())
            return
        
        if not HAS_ENGINE:
            self.wfile.write(json.dumps({
                'status': 'error',
                'error': 'Engine failed to load'
            }).encode())
            return
        
        if not url:
            self.wfile.write(json.dumps({
                'status': 'ready',
                'message': 'ssec-seo engine ready'
            }).encode())
            return
        
        # Run quick scan
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Quick scan config (fewer pages)
            config = ScanConfig(
                max_pages=5,
                concurrent_requests=2,
                check_subdomains=False,
                check_ssl_tls=False,
                check_exposed_data=False
            )
            
            engine = UltimateSEOEngine(config)
            results = loop.run_until_complete(engine.scan(url))
            loop.close()
            
            # Return data in format frontend expects
            self.wfile.write(json.dumps({
                'status': 'success',
                'url': url,
                'pages_scanned': results['statistics']['pages_crawled'],
                'total_issues': results['statistics']['total_issues'],
                'critical_issues': results['statistics']['critical_issues'],
                'high_issues': results['statistics']['high_issues'],
                'medium_issues': results['statistics']['medium_issues'],
                'low_issues': results['statistics']['low_issues'],
                'score': results['summary']['overall_score'],
                'risk_level': results['summary']['risk_level']
            }).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps({
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc()
            }).encode())
    
    def do_POST(self):
        """Handle POST requests - Full scan with HTML report"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if not HAS_ENGINE:
            self.wfile.write("<h1>Error: Engine not loaded</h1>".encode())
            return
        
        # Get POST data
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode())
            url = data.get('url')
            
            if not url:
                self.wfile.write("<h1>Error: Missing URL</h1>".encode())
                return
            
            # Run full scan
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Full scan config (more pages, all checks)
            config = ScanConfig(
                max_pages=20,
                concurrent_requests=5,
                check_subdomains=True,
                check_ssl_tls=True,
                check_exposed_data=True,
                check_misconfigurations=True,
                check_dead_links=True
            )
            
            engine = UltimateSEOEngine(config)
            results = loop.run_until_complete(engine.scan(url))
            
            # Generate HTML report
            report_html = engine.generate_report('html')
            loop.close()
            
            self.wfile.write(report_html.encode())
            
        except Exception as e:
            self.wfile.write(f"<h1>Error: {str(e)}</h1>".encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()