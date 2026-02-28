"""
ssec-seo API for Vercel - Ultimate Debug Version
"""
import sys
import os
import json
import asyncio
import importlib.util
import traceback
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Get the absolute path to the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
debug_info = {
    'project_root': project_root,
    'paths': [],
    'files': {},
    'import_attempts': [],
    'dependencies': {}
}

# Add paths and check files
paths_to_check = [
    project_root,
    os.path.join(project_root, 'ssec_seo'),
    os.path.join(project_root, 'ssec_seo', 'core'),
]

for path in paths_to_check:
    sys.path.insert(0, path)
    debug_info['paths'].append(str(path))
    if os.path.exists(path):
        debug_info['files'][str(path)] = os.listdir(path)[:10]  # First 10 files

# Check specific files
core_dir = os.path.join(project_root, 'ssec_seo', 'core')
files_to_check = {
    'ultimate_engine.py': os.path.join(core_dir, 'ultimate_engine.py'),
    'config.py': os.path.join(core_dir, 'config.py'),
    '__init__.py': os.path.join(core_dir, '__init__.py'),
}

for name, path in files_to_check.items():
    debug_info['files'][name] = os.path.exists(path)

# Try to check dependencies
try:
    import aiohttp
    debug_info['dependencies']['aiohttp'] = aiohttp.__version__
except ImportError as e:
    debug_info['dependencies']['aiohttp'] = f"Missing: {e}"

try:
    import bs4
    debug_info['dependencies']['beautifulsoup4'] = bs4.__version__
except ImportError as e:
    debug_info['dependencies']['beautifulsoup4'] = f"Missing: {e}"

try:
    import lxml
    debug_info['dependencies']['lxml'] = lxml.__version__
except ImportError as e:
    debug_info['dependencies']['lxml'] = f"Missing: {e}"

# Direct file imports using importlib
def import_from_path(module_name, file_path):
    """Import a module from file path with debug"""
    debug_info['import_attempts'].append({
        'module': module_name,
        'path': file_path,
        'exists': os.path.exists(file_path)
    })
    
    if not os.path.exists(file_path):
        return None
    
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        debug_info['import_attempts'][-1]['success'] = True
        return module
    except Exception as e:
        debug_info['import_attempts'][-1]['success'] = False
        debug_info['import_attempts'][-1]['error'] = str(e)
        debug_info['import_attempts'][-1]['traceback'] = traceback.format_exc()
        return None

# Import core modules
ultimate_module = import_from_path('ultimate_engine', files_to_check['ultimate_engine.py'])
config_module = import_from_path('config', files_to_check['config.py'])

if ultimate_module and config_module:
    try:
        UltimateSEOEngine = ultimate_module.UltimateSEOEngine
        ScanConfig = config_module.ScanConfig
        HAS_ENGINE = True
        debug_info['engine_status'] = 'loaded'
    except Exception as e:
        HAS_ENGINE = False
        debug_info['engine_status'] = f"Error accessing classes: {e}"
else:
    HAS_ENGINE = False
    debug_info['engine_status'] = 'modules_not_loaded'

class handler(BaseHTTPRequestHandler):
    """Handle HTTP requests"""
    
    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Parse URL
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        
        # If debug mode is requested, return debug info
        if 'debug' in query:
            self.wfile.write(json.dumps(debug_info, default=str, indent=2).encode())
            return
        
        # Check if engine is available
        if not HAS_ENGINE:
            self.wfile.write(json.dumps({
                'error': 'Engine not available',
                'debug': debug_info
            }, default=str).encode())
            return
        
        # Get URL parameter
        url = query.get('url', [None])[0]
        
        if not url:
            self.wfile.write(json.dumps({
                'status': 'ok',
                'message': 'ssec-seo API is running',
                'version': '0.1.0',
                'debug_hint': 'Add ?debug=true to see debug info'
            }).encode())
            return
        
        # Run quick scan
        try:
            # Run async scan
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Create minimal config
            config = ScanConfig(
                max_pages=1,
                concurrent_requests=1,
                check_subdomains=False,
                check_ssl_tls=False,
                check_exposed_data=False
            )
            
            engine = UltimateSEOEngine(config)
            results = loop.run_until_complete(engine.scan(url))
            loop.close()
            
            self.wfile.write(json.dumps({
                'status': 'success',
                'url': url,
                'pages_scanned': results['statistics']['pages_crawled'],
                'total_issues': results['statistics']['total_issues']
            }).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps({
                'error': str(e),
                'traceback': traceback.format_exc()
            }).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if not HAS_ENGINE:
            self.wfile.write(json.dumps({'error': 'Engine not available'}).encode())
            return
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode())
            url = data.get('url')
            
            if not url:
                self.wfile.write(json.dumps({'error': 'Missing url'}).encode())
                return
            
            self.wfile.write(json.dumps({
                'status': 'success',
                'message': 'Scan started',
                'url': url
            }).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        """Handle CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
