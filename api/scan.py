"""
ssec-seo API for Vercel - REAL SEO ENGINE VERSION
Direct imports working in Vercel environment
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

# Add all necessary paths
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'ssec_seo'))
sys.path.insert(0, os.path.join(project_root, 'ssec_seo', 'core'))
sys.path.insert(0, os.path.join(project_root, 'ssec_seo', 'core', 'crawler'))
sys.path.insert(0, os.path.join(project_root, 'ssec_seo', 'core', 'scanners'))
sys.path.insert(0, os.path.join(project_root, 'ssec_seo', 'core', 'reporters'))

def import_from_path(module_name, file_path):
    """Import a module from file path - WORKS in Vercel"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Failed to import {module_name}: {e}")
        return None

# Import real engine components
HAS_REAL_ENGINE = False
UltimateSEOEngine = None
ScanConfig = None

try:
    # Import core modules directly from files
    core_path = os.path.join(project_root, 'ssec_seo', 'core')
    
    ultimate_module = import_from_path('ultimate_engine', 
        os.path.join(core_path, 'ultimate_engine.py'))
    config_module = import_from_path('config', 
        os.path.join(core_path, 'config.py'))
    
    if ultimate_module and config_module:
        UltimateSEOEngine = ultimate_module.UltimateSEOEngine
        ScanConfig = config_module.ScanConfig
        HAS_REAL_ENGINE = True
        print("✅ REAL SEO ENGINE LOADED SUCCESSFULLY")
    else:
        print("❌ Failed to load engine modules")
        
except Exception as e:
    print(f"❌ Engine import error: {e}")
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
        
        # Check if engine is available
        if not HAS_REAL_ENGINE:
            self.wfile.write(json.dumps({
                'status': 'error',
                'error': 'Real SEO engine not available',
                'message': 'Using mock data temporarily',
                'mock_data': self.generate_mock_data(query.get('url', [''])[0])
            }).encode())
            return
        
        # Get URL parameter
        url = query.get('url', [None])[0]
        
        if not url:
            self.wfile.write(json.dumps({
                'status': 'ok',
                'message': 'ssec-seo REAL engine is running',
                'version': '0.1.0'
            }).encode())
            return
        
        # Run real scan
        try:
            # Run async scan
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Configure scan (limited for API)
            config = ScanConfig(
                max_pages=5,
                concurrent_requests=2,
                check_subdomains=True,
                check_ssl_tls=True,
                check_exposed_data=True,
                check_misconfigurations=True,
                check_dead_links=True
            )
            
            engine = UltimateSEOEngine(config)
            results = loop.run_until_complete(engine.scan(url))
            loop.close()
            
            # Return real results
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
                'traceback': traceback.format_exc(),
                'mock_data': self.generate_mock_data(url)
            }).encode())
    
    def do_POST(self):
        """Handle POST requests - Full HTML report with real engine"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Get POST data
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode())
            url = data.get('url')
            
            if not url:
                self.wfile.write("<h1>Error: Missing URL</h1>".encode())
                return
            
            if not HAS_REAL_ENGINE:
                self.wfile.write(self.generate_mock_html(url).encode())
                return
            
            # Run real full scan
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            config = ScanConfig(
                max_pages=10,
                concurrent_requests=3
            )
            
            engine = UltimateSEOEngine(config)
            results = loop.run_until_complete(engine.scan(url))
            
            # Generate real HTML report
            report_html = engine.generate_report('html')
            loop.close()
            
            self.wfile.write(report_html.encode())
            
        except Exception as e:
            self.wfile.write(f"<h1>Error: {e}</h1>".encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def generate_mock_data(self, url):
        """Fallback mock data if real engine fails"""
        import random
        pages = random.randint(5, 50)
        critical = random.randint(0, 3)
        high = random.randint(1, 5)
        medium = random.randint(2, 8)
        low = random.randint(3, 10)
        total = critical + high + medium + low
        score = max(30, min(95, 100 - (critical * 10 + high * 3 + medium * 1)))
        
        risk = 'critical' if critical > 0 else 'high' if high > 2 else 'medium' if medium > 5 else 'low'
        
        return {
            'status': 'mock',
            'url': url,
            'pages_scanned': pages,
            'total_issues': total,
            'critical_issues': critical,
            'high_issues': high,
            'medium_issues': medium,
            'low_issues': low,
            'score': score,
            'risk_level': risk
        }
    
    def generate_mock_html(self, url):
        """Fallback mock HTML report"""
        import random
        score = random.randint(60, 95)
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>ssec-seo Report (Mock)</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #667eea; }}
        .score {{ font-size: 48px; color: #27ae60; }}
        .warning {{ background: #fff3cd; padding: 20px; border-radius: 10px; }}
    </style>
</head>
<body>
    <h1>🔍 ssec-seo SEO Report</h1>
    <div class="warning">
        ⚠️ Real engine loading failed - Showing mock data
    </div>
    <div class="score">Score: {score}/100</div>
    <h3>Issues Found:</h3>
    <ul>
        <li>🔴 Missing meta descriptions (3 pages)</li>
        <li>🟠 Broken links found (2 links)</li>
        <li>🟡 SSL certificate expires in 45 days</li>
        <li>🔵 Images missing alt text (12 images)</li>
    </ul>
    <p>Target URL: {url}</p>
</body>
</html>"""
