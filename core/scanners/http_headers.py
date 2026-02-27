"""
HTTP Security Headers Scanner
"""
import aiohttp
from typing import Dict, List

class HTTPHeadersScanner:
    """Analyze HTTP security headers"""
    
    def __init__(self):
        self.security_headers = {
            'strict-transport-security': {
                'name': 'HSTS',
                'description': 'Enforces HTTPS connections',
                'severity': 'medium'
            },
            'content-security-policy': {
                'name': 'CSP',
                'description': 'Prevents XSS and data injection',
                'severity': 'high'
            },
            'x-frame-options': {
                'name': 'X-Frame-Options',
                'description': 'Prevents clickjacking',
                'severity': 'medium'
            },
            'x-content-type-options': {
                'name': 'X-Content-Type-Options',
                'description': 'Prevents MIME type sniffing',
                'severity': 'low'
            },
            'referrer-policy': {
                'name': 'Referrer-Policy',
                'description': 'Controls referrer information',
                'severity': 'low'
            },
            'permissions-policy': {
                'name': 'Permissions-Policy',
                'description': 'Controls browser features',
                'severity': 'low'
            },
            'x-xss-protection': {
                'name': 'X-XSS-Protection',
                'description': 'Enables XSS filtering',
                'severity': 'low'
            },
            'cache-control': {
                'name': 'Cache-Control',
                'description': 'Caching directives',
                'severity': 'low'
            }
        }
    
    async def scan(self, url: str, session: aiohttp.ClientSession) -> Dict:
        """Scan HTTP headers for security issues"""
        results = {
            'url': url,
            'headers': {},
            'missing': [],
            'present': [],
            'issues': []
        }
        
        try:
            async with session.get(url, timeout=10, ssl=False) as response:
                headers = {k.lower(): v for k, v in response.headers.items()}
                results['headers'] = dict(headers)
                
                # Check each security header
                for header, info in self.security_headers.items():
                    if header in headers:
                        results['present'].append({
                            'header': info['name'],
                            'value': headers[header][:100],
                            'severity': info['severity']
                        })
                    else:
                        results['missing'].append({
                            'header': info['name'],
                            'severity': info['severity'],
                            'description': info['description']
                        })
                        
                        # Add as issue
                        results['issues'].append({
                            'type': 'missing_security_header',
                            'title': f"Missing {info['name']} header",
                            'severity': info['severity'],
                            'description': info['description'],
                            'url': url
                        })
                
                # Check server info exposure
                if 'server' in headers:
                    results['issues'].append({
                        'type': 'server_exposure',
                        'title': 'Server information exposed',
                        'severity': 'low',
                        'description': f"Server: {headers['server']}",
                        'url': url
                    })
                
        except Exception as e:
            results['error'] = str(e)
        
        return results
