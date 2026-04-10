"""
Admin endpoint for viewing logs (protected)
"""
from http.server import BaseHTTPRequestHandler
import json
import os
from logger import logger

ADMIN_KEY = os.environ.get('ADMIN_KEY', 'change-me-in-production')

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Check admin key
        auth = self.headers.get('Authorization', '')
        if auth != f'Bearer {ADMIN_KEY}':
            self.send_error(401, 'Unauthorized')
            return
        
        # Parse query
        from urllib.parse import parse_qs, urlparse
        query = parse_qs(urlparse(self.path).query)
        hours = int(query.get('hours', [24])[0])
        
        # Get logs
        logs = logger.get_logs(hours)
        
        # Summary stats
        summary = {
            'total_scans': len([l for l in logs if l.get('event_type') == 'scan']),
            'unique_domains': len(set(l.get('domain') for l in logs if l.get('domain'))),
            'errors': len([l for l in logs if l.get('event_type') == 'error']),
            'rate_limits': len([l for l in logs if l.get('event_type') == 'rate_limit'])
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            'summary': summary,
            'logs': logs[-100:]  # Last 100 entries
        }, indent=2).encode())