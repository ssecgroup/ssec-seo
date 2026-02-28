"""
ssec-seo API for Vercel - FINAL DEBUG
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

# Debug info
debug = {
    'core_dir': core_dir,
    'core_exists': os.path.exists(core_dir),
    'ultimate_file': os.path.join(core_dir, 'ultimate_engine.py'),
    'ultimate_exists': os.path.exists(os.path.join(core_dir, 'ultimate_engine.py')),
    'config_exists': os.path.exists(os.path.join(core_dir, 'config.py')),
    'python_path': sys.path[:5]
}

# Try to import with full error capture
HAS_ENGINE = False
UltimateSEOEngine = None
ScanConfig = None
import_error = None

try:
    # Method 1: Direct import
    from ultimate_engine import UltimateSEOEngine
    from config import ScanConfig
    HAS_ENGINE = True
    debug['import_method'] = 'direct_success'
except Exception as e1:
    debug['direct_error'] = str(e1)
    debug['direct_traceback'] = traceback.format_exc()
    
    try:
        # Method 2: Import module then get attribute
        import ultimate_engine
        import config
        UltimateSEOEngine = ultimate_engine.UltimateSEOEngine
        ScanConfig = config.ScanConfig
        HAS_ENGINE = True
        debug['import_method'] = 'module_success'
    except Exception as e2:
        debug['module_error'] = str(e2)
        debug['module_traceback'] = traceback.format_exc()
        
        try:
            # Method 3: Check what's in the module
            import ultimate_engine
            debug['module_attrs'] = dir(ultimate_engine)
        except Exception as e3:
            debug['attr_check_error'] = str(e3)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        
        # Return debug info if requested
        if 'debug' in query:
            self.wfile.write(json.dumps(debug, default=str, indent=2).encode())
            return
        
        url = query.get('url', [None])[0]
        
        if not HAS_ENGINE:
            self.wfile.write(json.dumps({
                'error': 'Engine failed to load',
                'debug': 'Add ?debug=true to see why'
            }).encode())
            return
        
        if not url:
            self.wfile.write(json.dumps({
                'status': 'ready',
                'message': 'Engine loaded'
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
                'pages': results['statistics']['pages_crawled']
            }).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()