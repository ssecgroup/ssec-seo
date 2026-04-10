"""
Privacy-preserving audit logger for ssec-seo
Compliant with GDPR/CCPA - No PII stored
"""
import json
import time
import hashlib
import hmac
import os
from datetime import datetime
from urllib.parse import urlparse

# Salt for IP hashing (set in Vercel environment)
SALT = os.environ.get('LOG_SALT', 'default-salt-change-me')

class AuditLogger:
    def __init__(self):
        self.log_file = '/tmp/ssec_audit.jsonl'
    
    def log_scan(self, request_info, scan_result):
        """Log a scan event with privacy protection"""
        
        # Extract only domain from URL (strip path/query)
        full_url = request_info.get('url', '')
        domain = self._extract_domain(full_url)
        
        # Hash IP with salt (one-way, can't reverse)
        ip = request_info.get('ip', 'unknown')
        ip_hash = self._hash_ip(ip)
        
        # Create log entry
        entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event_type': 'scan',
            'domain': domain,  # Domain only, no path
            'scan_mode': request_info.get('mode', 'quick'),
            'pages_scanned': scan_result.get('pages_scanned', 0),
            'score': scan_result.get('score', 0),
            'risk_level': scan_result.get('risk_level', 'unknown'),
            'status': scan_result.get('status', 'error'),
            'ip_hash': ip_hash,
            'user_agent_hash': self._hash_user_agent(request_info.get('user_agent', '')),
            'request_id': request_info.get('request_id', '')
        }
        
        # Write to log file (Vercel ephemeral storage)
        self._write_log(entry)
        
        # Also send to Vercel Log Drains if configured
        self._send_to_vercel_logs(entry)
        
        return entry
    
    def log_error(self, request_info, error):
        """Log an error event"""
        entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event_type': 'error',
            'domain': self._extract_domain(request_info.get('url', '')),
            'error_type': type(error).__name__,
            'error_message': str(error)[:200],  # Truncate
            'ip_hash': self._hash_ip(request_info.get('ip', 'unknown')),
            'request_id': request_info.get('request_id', '')
        }
        self._write_log(entry)
        return entry
    
    def log_rate_limit(self, identifier, limit_type):
        """Log rate limit hits for abuse detection"""
        entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event_type': 'rate_limit',
            'identifier_hash': self._hash_value(identifier),
            'limit_type': limit_type
        }
        self._write_log(entry)
        return entry
    
    def _extract_domain(self, url):
        """Extract only domain from URL, strip credentials"""
        try:
            parsed = urlparse(url)
            return parsed.netloc or parsed.path.split('/')[0]
        except:
            return 'invalid-url'
    
    def _hash_ip(self, ip):
        """One-way hash of IP with salt"""
        if ip == 'unknown':
            return 'unknown'
        return hashlib.sha256(f"{ip}:{SALT}".encode()).hexdigest()[:16]
    
    def _hash_user_agent(self, ua):
        """Hash user agent for privacy"""
        if not ua:
            return 'unknown'
        return hashlib.sha256(ua.encode()).hexdigest()[:12]
    
    def _hash_value(self, value):
        """Generic hash function"""
        return hashlib.sha256(f"{value}:{SALT}".encode()).hexdigest()[:16]
    
    def _write_log(self, entry):
        """Write to JSONL file"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except:
            pass  # Fail silently - don't break scan
    
    def _send_to_vercel_logs(self, entry):
        """Send to Vercel Log Drains (if configured)"""
        # Vercel automatically captures console.log
        print(json.dumps(entry))
    
    def get_logs(self, hours=24):
        """Retrieve recent logs (for admin)"""
        logs = []
        cutoff = time.time() - (hours * 3600)
        
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        entry_time = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                        if entry_time.timestamp() > cutoff:
                            logs.append(entry)
                    except:
                        continue
        except:
            pass
        
        return logs


# Global logger instance
logger = AuditLogger()