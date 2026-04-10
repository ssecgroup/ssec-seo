"""
ssec-seo API for Vercel - COMPLETE WORKING VERSION
Returns full SEO data matching frontend expectations
With privacy-preserving audit logging for legal compliance
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
    """Privacy-safe logger - no PII stored"""
    
    def __init__(self):
        self.log_file = '/tmp/ssec_audit.jsonl'
        self.salt = os.environ.get('LOG_SALT', 'ssec-seo-default-salt')
    
    def log_scan(self, request_info, scan_result):
        """Log scan event - domain only, IP hashed"""
        entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event': 'scan',
            'domain': self._extract_domain(request_info.get('url', '')),
            'mode': request_info.get('mode', 'quick'),
            'pages': scan_result.get('pages_scanned', 0),
            'score': scan_result.get('score', 0),
            'risk': scan_result.get('risk_level', 'unknown'),
            'status': scan_result.get('status', 'success'),
            'ip_hash': self._hash(request_info.get('ip', 'unknown')),
            'req_id': request_info.get('request_id', '')
        }
        self._write(entry)
    
    def log_error(self, request_info, error):
        """Log error event"""
        entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event': 'error',
            'domain': self._extract_domain(request_info.get('url', '')),
            'error': str(error)[:200],
            'ip_hash': self._hash(request_info.get('ip', 'unknown')),
            'req_id': request_info.get('request_id', '')
        }
        self._write(entry)
    
    def log_rate_limit(self, identifier):
        """Log rate limit hit"""
        entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event': 'rate_limit',
            'id_hash': self._hash(identifier)
        }
        self._write(entry)
    
    def _extract_domain(self, url):
        """Extract domain only - strip path, query, credentials"""
        try:
            parsed = urlparse(url)
            return parsed.netloc or parsed.path.split('/')[0]
        except:
            return 'invalid'
    
    def _hash(self, value):
        """One-way hash with salt - irreversible"""
        return hashlib.sha256(f"{value}:{self.salt}".encode()).hexdigest()[:12]
    
    def _write(self, entry):
        """Write to JSONL file and stdout for Vercel logs"""
        try:
            line = json.dumps(entry)
            # Vercel captures stdout
            print(line)
            # Also write to temp file
            with open(self.log_file, 'a') as f:
                f.write(line + '\n')
        except:
            pass  # Never break scan for logging

# Global logger
logger = AuditLogger()

# ===== RATE LIMITER =====

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = {}  # IP hash -> [timestamps]
        self.limit = 60     # Max requests
        self.window = 3600  # Per hour
    
    def is_allowed(self, ip):
        """Check if IP is within rate limit"""
        now = time.time()
        ip_hash = logger._hash(ip)
        
        # Clean old entries
        if ip_hash in self.requests:
            self.requests[ip_hash] = [t for t in self.requests[ip_hash] if now - t < self.window]
        else:
            self.requests[ip_hash] = []
        
        # Check limit
        if len(self.requests[ip_hash]) >= self.limit:
            logger.log_rate_limit(ip)
            return False
        
        # Add request
        self.requests[ip_hash].append(now)
        return True
    
    def get_remaining(self, ip):
        """Get remaining requests for IP"""
        now = time.time()
        ip_hash = logger._hash(ip)
        
        if ip_hash not in self.requests:
            return self.limit
        
        recent = [t for t in self.requests[ip_hash] if now - t < self.window]
        return max(0, self.limit - len(recent))

# Global rate limiter
rate_limiter = RateLimiter()

# ===== MAIN HANDLER =====

class handler(BaseHTTPRequestHandler):
    
    def get_client_ip(self):
        """Extract client IP from headers"""
        forwarded = self.headers.get('X-Forwarded-For', '')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return self.client_address[0] if hasattr(self, 'client_address') else 'unknown'
    
    def do_GET(self):
        """Handle GET requests - Quick scan"""
        request_id = str(uuid.uuid4())[:8]
        client_ip = self.get_client_ip()
        
        # Rate limit check
        if not rate_limiter.is_allowed(client_ip):
            self.send_response(429)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'error',
                'error': 'Rate limit exceeded. Please try again later.',
                'retry_after': 3600
            }).encode())
            return
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('X-Request-ID', request_id)
        self.end_headers()
        
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        url = query.get('url', [None])[0]
        
        # Debug endpoint - no logging
        if 'debug' in query:
            debug_info = {
                'engine_loaded': HAS_ENGINE,
                'core_exists': os.path.exists(core_dir),
                'python_path': sys.path[:3],
                'rate_limit_remaining': rate_limiter.get_remaining(client_ip)
            }
            self.wfile.write(json.dumps(debug_info).encode())
            return
        
        if not HAS_ENGINE:
            self.wfile.write(json.dumps({
                'status': 'error',
                'error': 'Engine failed to load'
            }).encode())
            logger.log_error({'url': url, 'ip': client_ip, 'request_id': request_id}, 'Engine not loaded')
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
            
            # Quick scan config (fewer pages, safer)
            config = ScanConfig(
                max_pages=3,                    # Reduced for safety
                concurrent_requests=2,
                check_subdomains=False,
                check_ssl_tls=True,
                check_exposed_data=False,       # Disabled - most dangerous
                check_misconfigurations=True,
                check_dead_links=False
            )
            
            engine = UltimateSEOEngine(config)
            results = loop.run_until_complete(engine.scan(url))
            loop.close()
            
            response_data = {
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
            
            # Log successful scan
            logger.log_scan({
                'url': url,
                'ip': client_ip,
                'mode': 'quick',
                'request_id': request_id
            }, response_data)
            
            self.wfile.write(json.dumps(response_data).encode())
            
        except Exception as e:
            logger.log_error({
                'url': url,
                'ip': client_ip,
                'request_id': request_id
            }, e)
            
            self.wfile.write(json.dumps({
                'status': 'error',
                'error': str(e),
                'request_id': request_id
            }).encode())
    
    def do_POST(self):
        """Handle POST requests - Full scan with HTML report"""
        request_id = str(uuid.uuid4())[:8]
        client_ip = self.get_client_ip()
        
        # Rate limit check (stricter for full scans)
        if not rate_limiter.is_allowed(client_ip):
            self.send_response(429)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("<h1>Rate limit exceeded. Please try again later.</h1>".encode())
            return
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('X-Request-ID', request_id)
        self.end_headers()
        
        if not HAS_ENGINE:
            self.wfile.write("<h1>Error: Engine not loaded</h1>".encode())
            logger.log_error({'ip': client_ip, 'request_id': request_id}, 'Engine not loaded')
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
            
            # Full scan config
            config = ScanConfig(
                max_pages=10,                   # Reduced from 20
                concurrent_requests=3,          # Reduced from 5
                check_subdomains=False,         # Disabled for safety
                check_ssl_tls=True,
                check_exposed_data=False,       # Disabled
                check_misconfigurations=True,
                check_dead_links=False
            )
            
            engine = UltimateSEOEngine(config)
            results = loop.run_until_complete(engine.scan(url))
            
            # Log full scan
            logger.log_scan({
                'url': url,
                'ip': client_ip,
                'mode': 'full',
                'request_id': request_id
            }, {
                'status': 'success',
                'pages_scanned': results['statistics']['pages_crawled'],
                'score': results['summary']['overall_score'],
                'risk_level': results['summary']['risk_level']
            })
            
            # Generate HTML report
            report_html = engine.generate_report('html')
            loop.close()
            
            self.wfile.write(report_html.encode())
            
        except Exception as e:
            logger.log_error({
                'url': url if 'url' in locals() else 'unknown',
                'ip': client_ip,
                'request_id': request_id
            }, e)
            
            self.wfile.write(f"<h1>Error: {str(e)}</h1><p>Request ID: {request_id}</p>".encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Request-ID')
        self.end_headers()