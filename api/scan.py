"""
ssec-seo API for Vercel - SAFE VERSION
Returns full SEO data matching frontend expectations
With privacy-preserving audit logging and safe defaults
"""
import sys
import os
import json
import asyncio
import traceback
import uuid
import hashlib
import time
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from datetime import datetime

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

# ===== PRIVACY-PRESERVING AUDIT LOGGER =====
class AuditLogger:
    def __init__(self):
        self.salt = os.environ.get('LOG_SALT', 'ssec-seo-default-salt')
    
    def log_scan(self, request_info, scan_result):
        entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event': 'scan',
            'domain': self._extract_domain(request_info.get('url', '')),
            'mode': request_info.get('mode', 'quick'),
            'pages': scan_result.get('pages_scanned', 0),
            'score': scan_result.get('score', 0),
            'ip_hash': self._hash(request_info.get('ip', 'unknown'))
        }
        print(json.dumps(entry))
    
    def _extract_domain(self, url):
        try:
            parsed = urlparse(url)
            return parsed.netloc or parsed.path.split('/')[0]
        except:
            return 'invalid'
    
    def _hash(self, value):
        return hashlib.sha256(f"{value}:{self.salt}".encode()).hexdigest()[:12]

logger = AuditLogger()

# ===== RATE LIMITER =====
class RateLimiter:
    def __init__(self):
        self.requests = {}
        self.limit = 60
        self.window = 3600
    
    def is_allowed(self, ip):
        now = time.time()
        ip_hash = logger._hash(ip)
        if ip_hash not in self.requests:
            self.requests[ip_hash] = []
        self.requests[ip_hash] = [t for t in self.requests[ip_hash] if now - t < self.window]
        if len(self.requests[ip_hash]) >= self.limit:
            return False
        self.requests[ip_hash].append(now)
        return True

rate_limiter = RateLimiter()

class handler(BaseHTTPRequestHandler):
    def get_client_ip(self):
        forwarded = self.headers.get('X-Forwarded-For', '')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return 'unknown'
    
    def do_GET(self):
        """Handle GET requests - Quick scan (SAFE MODE)"""
        client_ip = self.get_client_ip()
        
        # Rate limit check
        if not rate_limiter.is_allowed(client_ip):
            self.send_response(429)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'error', 'error': 'Rate limit exceeded'}).encode())
            return
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        url = query.get('url', [None])[0]
        
        if 'debug' in query:
            self.wfile.write(json.dumps({
                'engine_loaded': HAS_ENGINE,
                'core_exists': os.path.exists(core_dir),
                'safe_mode': True
            }).encode())
            return
        
        if not HAS_ENGINE:
            self.wfile.write(json.dumps({'status': 'error', 'error': 'Engine failed'}).encode())
            return
        
        if not url:
            self.wfile.write(json.dumps({'status': 'ready', 'message': 'ssec-seo ready'}).encode())
            return
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # ===== SAFE QUICK SCAN CONFIG =====
            config = ScanConfig(
                max_pages=3,                    # REDUCED from 5
                concurrent_requests=2,
                check_subdomains=False,         # SAFE
                check_ssl_tls=True,             # SAFE
                check_exposed_data=False,       # SAFE - DISABLED
                check_misconfigurations=True,   # SAFE
                check_dead_links=False          # SAFE - DISABLED
            )
            
            engine = UltimateSEOEngine(config)
            results = loop.run_until_complete(engine.scan(url))
            loop.close()
            
            response = {
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
            }
            
            logger.log_scan({'url': url, 'ip': client_ip, 'mode': 'quick'}, response)
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps({'status': 'error', 'error': str(e)}).encode())
    
    def do_POST(self):
        """Handle POST requests - Full scan (SAFE MODE)"""
        client_ip = self.get_client_ip()
        
        if not rate_limiter.is_allowed(client_ip):
            self.send_response(429)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("<h1>Rate limit exceeded</h1>".encode())
            return
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if not HAS_ENGINE:
            self.wfile.write("<h1>Error: Engine not loaded</h1>".encode())
            return
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode())
            url = data.get('url')
            
            if not url:
                self.wfile.write("<h1>Error: Missing URL</h1>".encode())
                return
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # ===== SAFE FULL SCAN CONFIG =====
            config = ScanConfig(
                max_pages=10,                   # REDUCED from 20
                concurrent_requests=3,          # REDUCED from 5
                check_subdomains=False,         # SAFE - DISABLED
                check_ssl_tls=True,             # SAFE
                check_exposed_data=False,       # SAFE - DISABLED (DANGEROUS!)
                check_misconfigurations=True,   # SAFE
                check_dead_links=False          # SAFE - DISABLED
            )
            
            engine = UltimateSEOEngine(config)
            results = loop.run_until_complete(engine.scan(url))
            
            logger.log_scan({'url': url, 'ip': client_ip, 'mode': 'full'}, {
                'pages_scanned': results['statistics']['pages_crawled'],
                'score': results['summary']['overall_score']
            })
            
            report_html = engine.generate_report('html')
            loop.close()
            
            self.wfile.write(report_html.encode())
            
        except Exception as e:
            self.wfile.write(f"<h1>Error: {str(e)}</h1>".encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
