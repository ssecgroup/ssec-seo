"""
ssec-seo API for Vercel - REAL SEO ENGINE VERSION with correct paths
"""
import sys
import os
import json
import asyncio
import importlib.util
import traceback
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Get project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add paths (NO 'ssec_seo' folder - direct core path)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'core'))
sys.path.insert(0, os.path.join(project_root, 'core', 'crawler'))
sys.path.insert(0, os.path.join(project_root, 'core', 'scanners'))
sys.path.insert(0, os.path.join(project_root, 'core', 'reporters'))

def import_from_path(module_name, file_path):
    """Import a module from file path"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Failed to import {module_name}: {e}")
        return None

# Import real engine components - DIRECT from core path
HAS_REAL_ENGINE = False
UltimateSEOEngine = None
ScanConfig = None

try:
    # Import directly from core directory (NO 'ssec_seo' folder)
    core_path = os.path.join(project_root, 'core')
    
    ultimate_module = import_from_path('ultimate_engine', 
        os.path.join(core_path, 'ultimate_engine.py'))
    config_module = import_from_path('config', 
        os.path.join(core_path, 'config.py'))
    
    if ultimate_module and config_module:
        UltimateSEOEngine = ultimate_module.UltimateSEOEngine
        ScanConfig = config_module.ScanConfig
        HAS_REAL_ENGINE = True
        print(" REAL SEO ENGINE LOADED SUCCESSFULLY")
    else:
        print(" Failed to load engine modules")
        
except Exception as e:
    print(f" Engine import error: {e}")
    traceback.print_exc()

class handler(BaseHTTPRequestHandler):
    """Handle HTTP requests with REAL SEO engine"""
    
    def do_GET(self):
        """Handle GET requests - Quick scan with real engine"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Parse URL
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        
        # If debug parameter, show paths
        if 'debug' in query:
            self.wfile.write(json.dumps({
                'project_root': project_root,
                'core_exists': os.path.exists(os.path.join(project_root, 'core')),
                'ultimate_exists': os.path.exists(os.path.join(project_root, 'core', 'ultimate_engine.py')),
                'python_path': sys.path[:5]
            }).encode())
            return
        
        if not HAS_REAL_ENGINE:
            self.wfile.write(json.dumps({
                'status': 'error',
                'error': 'Real SEO engine not available',
                'message': 'Using mock data',
                'mock_data': self.generate_mock_data(query.get('url', [''])[0])
            }).encode())
            return
        
        # Get URL parameter
        url = query.get('url', [None])[0]
        
        if not url:
            self.wfile.write(json.dumps({
                'status': 'ok',
                'message': 'ssec-seo REAL engine is running'
            }).encode())
            return
        
        # Run real scan
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
                'pages_scanned': results['statistics']['pages_crawled'],
                'total_issues': results['statistics']['total_issues'],
                'critical_issues': results['statistics']['critical_issues']
            }).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps({
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc(),
                'mock_data': self.generate_mock_data(url)
            }).encode())
    
    def generate_mock_data(self, url):
        """Fallback mock data"""
        import random
        return {
            'status': 'mock',
            'url': url,
            'pages_scanned': random.randint(5, 20),
            'total_issues': random.randint(5, 30),
            'critical_issues': random.randint(0, 3)
        }
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()