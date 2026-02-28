"""
ssec-seo API for Vercel - ULTIMATE DEBUG VERSION
"""
import sys
import os
import json
import asyncio
import traceback
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Get paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
core_path = os.path.join(project_root, 'core')

# Add to path
sys.path.insert(0, core_path)

# Comprehensive debug info
debug_info = {
    'project_root': project_root,
    'core_path': core_path,
    'core_exists': os.path.exists(core_path),
    'files_in_core': os.listdir(core_path) if os.path.exists(core_path) else [],
    'python_path': sys.path[:5],
    'import_attempts': []
}

# Try to import with detailed error tracking
HAS_REAL_ENGINE = False
UltimateSEOEngine = None
ScanConfig = None

# Check if files exist
ultimate_file = os.path.join(core_path, 'ultimate_engine.py')
config_file = os.path.join(core_path, 'config.py')

debug_info['ultimate_exists'] = os.path.exists(ultimate_file)
debug_info['config_exists'] = os.path.exists(config_file)

if debug_info['ultimate_exists'] and debug_info['config_exists']:
    try:
        # Method 1: Direct import
        from ultimate_engine import UltimateSEOEngine
        from config import ScanConfig
        HAS_REAL_ENGINE = True
        debug_info['import_attempts'].append({'method': 'direct', 'success': True})
    except Exception as e1:
        debug_info['import_attempts'].append({'method': 'direct', 'success': False, 'error': str(e1)})
        
        try:
            # Method 2: Import with full path
            import importlib.util
            spec = importlib.util.spec_from_file_location('ultimate_engine', ultimate_file)
            ultimate_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ultimate_module)
            UltimateSEOEngine = ultimate_module.UltimateSEOEngine
            
            spec2 = importlib.util.spec_from_file_location('config', config_file)
            config_module = importlib.util.module_from_spec(spec2)
            spec2.loader.exec_module(config_module)
            ScanConfig = config_module.ScanConfig
            
            HAS_REAL_ENGINE = True
            debug_info['import_attempts'].append({'method': 'file_import', 'success': True})
        except Exception as e2:
            debug_info['import_attempts'].append({'method': 'file_import', 'success': False, 'error': str(e2), 'traceback': traceback.format_exc()})

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        
        # If debug=true, return full debug info
        if 'debug' in query:
            self.wfile.write(json.dumps(debug_info, default=str, indent=2).encode())
            return
        
        url = query.get('url', [None])[0]
        
        if not HAS_REAL_ENGINE:
            self.wfile.write(json.dumps({
                'status': 'error',
                'error': 'Engine not loaded',
                'debug_hint': 'Add ?debug=true to see why',
                'mock': self.generate_mock_data(url or 'no-url')
            }).encode())
            return
        
        if not url:
            self.wfile.write(json.dumps({'status': 'ok', 'message': 'ssec-seo ready'}).encode())
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
                'issues': results['statistics']['total_issues']
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