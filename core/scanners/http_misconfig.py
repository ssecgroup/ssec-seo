"""
HTTP misconfiguration and security scanner
"""
import aiohttp
from urllib.parse import urljoin
import asyncio

class HTTPMisconfigScanner:
    """Find HTTP misconfigurations and security issues"""
    
    def __init__(self):
        self.sensitive_paths = [
            # Version control
            '/.git/config',
            '/.git/HEAD',
            '/.svn/entries',
            '/.svn/wc.db',
            '/.hg/',
            '/.bzr/',
            
            # Environment files
            '/.env',
            '/.env.local',
            '/.env.production',
            '/.env.development',
            '/.env.staging',
            '/.env.example',
            
            # Config files
            '/wp-config.php',
            '/wp-config.bak',
            '/wp-config.old',
            '/config.php',
            '/configuration.php',
            '/settings.php',
            '/config.json',
            '/config.yml',
            '/config.yaml',
            '/database.yml',
            '/database.yaml',
            '/parameters.yml',
            '/app/config/parameters.yml',
            
            # Backup files
            '/backup.zip',
            '/backup.tar.gz',
            '/backup.sql',
            '/dump.sql',
            '/db.sql',
            '/database.sql',
            '/site_backup.zip',
            '/site.tar.gz',
            '/www.zip',
            '/www.tar.gz',
            
            # Log files
            '/logs/error.log',
            '/logs/access.log',
            '/error.log',
            '/access.log',
            '/debug.log',
            '/log.txt',
            '/logs.txt',
            
            # Admin panels
            '/admin/',
            '/administrator/',
            '/wp-admin/',
            '/backend/',
            '/cpanel/',
            '/phpmyadmin/',
            '/phpPgAdmin/',
            '/adminer/',
            '/mysql/',
            '/myadmin/',
            '/pgadmin/',
            
            # API endpoints
            '/api/',
            '/api/v1/',
            '/api/v2/',
            '/graphql',
            '/graphiql',
            '/swagger/',
            '/swagger-ui/',
            '/api-docs/',
            '/docs/',
            
            # Sensitive files
            '/phpinfo.php',
            '/info.php',
            '/test.php',
            '/.htaccess',
            '/.htpasswd',
            '/.aws/credentials',
            '/.aws/config',
            '/.azure/credentials',
            '/.gcloud/credentials',
            
            # Old versions
            '/old/',
            '/backup/',
            '/bak/',
            '/temp/',
            '/tmp/',
            '/test/',
            '/tests/',
            '/testing/',
            '/staging/',
            '/dev/',
            '/development/',
            
            # Common directories
            '/uploads/',
            '/images/',
            '/img/',
            '/css/',
            '/js/',
            '/assets/',
            '/static/',
            '/public/',
            '/private/',
            '/files/',
            '/download/',
            '/downloads/',
        ]
        
        self.methods_to_test = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH', 'TRACE']
        
    async def scan(self, base_url: str, session: aiohttp.ClientSession) -> dict:
        """Comprehensive HTTP misconfiguration scan"""
        results = {
            'exposed_paths': [],
            'methods_allowed': {},
            'misconfigurations': [],
            'directory_listing': [],
            'security_issues': []
        }
        
        # Check exposed sensitive paths
        results['exposed_paths'] = await self._check_sensitive_paths(base_url, session)
        
        # Check HTTP methods
        results['methods_allowed'] = await self._check_http_methods(base_url, session)
        
        # Check directory listing
        results['directory_listing'] = await self._check_directory_listing(base_url, session)
        
        # Check security headers
        results['security_issues'] = await self._check_security_headers(base_url, session)
        
        return results
    
    async def _check_sensitive_paths(self, base_url: str, session: aiohttp.ClientSession) -> list:
        """Check for exposed sensitive paths"""
        found = []
        
        async def check_path(path):
            url = urljoin(base_url, path)
            try:
                async with session.get(url, timeout=5, allow_redirects=False) as response:
                    if response.status == 200:
                        # Check content for sensitivity
                        content = await response.text()
                        finding = {
                            'url': url,
                            'status': response.status,
                            'type': 'exposed_path',
                            'severity': self._assess_severity(path, content),
                            'content_type': response.headers.get('content-type', '')
                        }
                        
                        # Check if it's a directory listing
                        if '<title>Index of' in content or 'Parent Directory' in content:
                            finding['type'] = 'directory_listing'
                            finding['severity'] = 'high'
                        
                        found.append(finding)
                        print(f"⚠️  Found: {url}")
                        
            except Exception as e:
                if '404' not in str(e):
                    pass
            return None
        
        # Check paths in batches
        batch_size = 20
        for i in range(0, len(self.sensitive_paths), batch_size):
            batch = self.sensitive_paths[i:i+batch_size]
            tasks = [check_path(path) for path in batch]
            await asyncio.gather(*tasks)
        
        return found
    
    def _assess_severity(self, path: str, content: str) -> str:
        """Assess severity of exposed path"""
        # Critical patterns
        critical_patterns = [
            '.git', '.env', 'wp-config', 'config.php',
            'password', 'secret', 'key', 'token',
            'database', 'mysql', 'postgres',
            'aws', 'azure', 'gcloud'
        ]
        
        for pattern in critical_patterns:
            if pattern in path.lower() or pattern in content.lower():
                return 'critical'
        
        # High severity
        high_patterns = [
            'backup', 'dump', 'sql', 'log', 'admin',
            'phpmyadmin', 'phpinfo'
        ]
        
        for pattern in high_patterns:
            if pattern in path.lower():
                return 'high'
        
        # Medium severity
        medium_patterns = ['old', 'temp', 'test', 'dev', 'staging']
        
        for pattern in medium_patterns:
            if pattern in path.lower():
                return 'medium'
        
        return 'low'
    
    async def _check_http_methods(self, base_url: str, session: aiohttp.ClientSession) -> dict:
        """Check allowed HTTP methods"""
        methods_allowed = {}
        
        for method in self.methods_to_test:
            try:
                async with session.request(method, base_url, timeout=5) as response:
                    if response.status not in [405, 501]:  # Method not allowed/not implemented
                        methods_allowed[method] = {
                            'allowed': True,
                            'status': response.status
                        }
                    else:
                        methods_allowed[method] = {
                            'allowed': False,
                            'status': response.status
                        }
            except:
                methods_allowed[method] = {
                    'allowed': False,
                    'error': 'Connection failed'
                }
        
        return methods_allowed
    
    async def _check_directory_listing(self, base_url: str, session: aiohttp.ClientSession) -> list:
        """Check for directory listing vulnerabilities"""
        directories = [
            '/images/', '/css/', '/js/', '/assets/', '/static/',
            '/uploads/', '/files/', '/downloads/', '/backup/',
            '/old/', '/temp/', '/tmp/', '/test/', '/admin/'
        ]
        
        found = []
        
        for directory in directories:
            url = urljoin(base_url, directory)
            try:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        content = await response.text()
                        if '<title>Index of' in content or 'Parent Directory' in content:
                            found.append({
                                'url': url,
                                'type': 'directory_listing',
                                'severity': 'high',
                                'description': f'Directory listing enabled at {directory}'
                            })
            except:
                pass
        
        return found
    
    async def _check_security_headers(self, base_url: str, session: aiohttp.ClientSession) -> list:
        """Check for missing security headers"""
        try:
            async with session.get(base_url, timeout=5) as response:
                headers = response.headers
                
                security_headers = {
                    'Strict-Transport-Security': {
                        'required': True,
                        'severity': 'medium',
                        'description': 'HSTS header missing - encourages HTTPS usage'
                    },
                    'Content-Security-Policy': {
                        'required': True,
                        'severity': 'medium',
                        'description': 'CSP header missing - helps prevent XSS attacks'
                    },
                    'X-Frame-Options': {
                        'required': True,
                        'severity': 'medium',
                        'description': 'X-Frame-Options missing - clickjacking risk'
                    },
                    'X-Content-Type-Options': {
                        'required': True,
                        'severity': 'low',
                        'description': 'X-Content-Type-Options missing - MIME sniffing risk'
                    },
                    'X-XSS-Protection': {
                        'required': False,
                        'severity': 'low',
                        'description': 'X-XSS-Protection missing - XSS filter not enabled'
                    },
                    'Referrer-Policy': {
                        'required': False,
                        'severity': 'low',
                        'description': 'Referrer-Policy missing - information disclosure risk'
                    },
                    'Permissions-Policy': {
                        'required': False,
                        'severity': 'low',
                        'description': 'Permissions-Policy missing - feature control not set'
                    }
                }
                
                issues = []
                for header, info in security_headers.items():
                    if info['required'] and header not in headers:
                        issues.append({
                            'type': 'missing_security_header',
                            'header': header,
                            'severity': info['severity'],
                            'description': info['description']
                        })
                
                return issues
                
        except Exception as e:
            return [{
                'type': 'security_check_failed',
                'severity': 'low',
                'description': f'Could not check security headers: {str(e)}'
            }]
