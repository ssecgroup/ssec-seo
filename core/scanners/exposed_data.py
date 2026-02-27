"""
Scanner for exposed sensitive data
"""
import aiohttp
from urllib.parse import urljoin
import re

class ExposedDataScanner:
    """Find exposed files, directories, and sensitive data"""
    
    def __init__(self):
        self.common_paths = [
            # Version control
            '/.git/',
            '/.git/config',
            '/.git/HEAD',
            '/.svn/',
            '/.env',
            '/.env.local',
            '/.env.production',
            
            # Backups
            '/backup/',
            '/backups/',
            '/bak/',
            '/old/',
            '/backup.sql',
            '/database.sql',
            '/db.sql',
            
            # Config files
            '/wp-config.php',
            '/config.php',
            '/configuration.php',
            '/settings.py',
            '/config.json',
            
            # Admin panels
            '/admin/',
            '/administrator/',
            '/wp-admin/',
            '/backend/',
            
            # API docs
            '/api/docs',
            '/swagger',
            '/api/swagger',
            '/graphql',
            '/api/graphql',
            
            # Sensitive files
            '/phpinfo.php',
            '/info.php',
            '/test.php',
            '/.htaccess',
            '/.htpasswd',
            
            # Logs
            '/logs/',
            '/error.log',
            '/access.log',
            '/debug.log',
            
            # Common files
            '/robots.txt',
            '/sitemap.xml',
            '/crossdomain.xml',
            '/.well-known/',
            
            # Old versions
            '/old/',
            '/backup/',
            '/archive/',
            '/v1/',
            '/v2/',
        ]
        
        self.sensitive_patterns = {
            'aws_key': r'AKIA[0-9A-Z]{16}',
            'api_key': r'api[_-]?key[\s]*[=:][\s]*["\'][0-9a-zA-Z]{32}["\']',
            'jwt': r'eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}',
            'password': r'password[\s]*[=:][\s]*["\'][^"\']+["\']',
            'database_url': r'(postgresql|mysql|mongodb)://[^"\'\s]+',
            'private_key': r'-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----',
        }
    
    async def scan(self, base_url: str, session: aiohttp.ClientSession) -> list:
        """Scan for exposed data"""
        findings = []
        
        for path in self.common_paths:
            url = urljoin(base_url, path)
            try:
                async with session.get(url, timeout=5, ssl=False) as response:
                    if response.status == 200:
                        # Read first few KB to check content
                        content = await response.content.read(8192)
                        content_str = content.decode('utf-8', errors='ignore')
                        
                        # Check for sensitive patterns
                        sensitive_data = self._check_sensitive_patterns(content_str)
                        
                        finding = {
                            'url': url,
                            'status': response.status,
                            'type': 'exposed_path',
                            'severity': self._get_severity(path, sensitive_data),
                            'content_type': response.headers.get('content-type', ''),
                            'sensitive_data': sensitive_data,
                            'description': f"Exposed path: {path}"
                        }
                        findings.append(finding)
                        print(f"⚠️  Found exposed: {url}")
            except:
                continue
                
        return findings
    
    def _check_sensitive_patterns(self, content: str) -> list:
        """Check content for sensitive data patterns"""
        found = []
        for pattern_name, pattern in self.sensitive_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                found.append(pattern_name)
        return found
    
    def _get_severity(self, path: str, sensitive_data: list) -> str:
        """Determine severity level"""
        if sensitive_data:
            return 'critical'
        if any(x in path for x in ['.git', '.env', 'wp-config', 'config']):
            return 'high'
        if any(x in path for x in ['backup', 'old', 'sql']):
            return 'medium'
        return 'low'
