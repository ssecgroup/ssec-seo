"""
Security vulnerability scanner
"""
import aiohttp
from urllib.parse import urljoin
import asyncio
from typing import List, Dict

class SecurityScanner:
    """Check for common security vulnerabilities"""
    
    def __init__(self):
        self.common_paths = [
            '/.well-known/security.txt',
            '/security.txt',
            '/crossdomain.xml',
            '/clientaccesspolicy.xml',
            '/sitemap.xml',
            '/robots.txt',
            '/.htaccess',
            '/web.config',
            '/.git/config',
            '/.env',
            '/phpinfo.php',
            '/info.php',
            '/test.php',
            '/wp-config.php',
            '/config.php',
            '/backup.sql',
            '/dump.sql'
        ]
        
        self.admin_paths = [
            '/admin',
            '/administrator',
            '/wp-admin',
            '/backend',
            '/cpanel',
            '/phpmyadmin',
            '/myadmin',
            '/adminer',
            '/login',
            '/wp-login.php'
        ]
    
    async def scan(self, base_url: str, session: aiohttp.ClientSession) -> Dict:
        """Scan for security issues"""
        results = {
            'exposed_paths': [],
            'admin_panels': [],
            'security_txt': None,
            'issues': []
        }
        
        # Check security.txt
        security_txt_url = urljoin(base_url, '/.well-known/security.txt')
        try:
            async with session.get(security_txt_url, timeout=5) as response:
                if response.status == 200:
                    content = await response.text()
                    results['security_txt'] = {
                        'url': security_txt_url,
                        'content': content[:500]
                    }
                    print("  ✅ Found security.txt")
        except:
            results['issues'].append({
                'type': 'missing_security_txt',
                'severity': 'low',
                'description': 'No security.txt file found for vulnerability disclosure',
                'url': base_url
            })
        
        # Check common paths
        async def check_path(path):
            url = urljoin(base_url, path)
            try:
                async with session.get(url, timeout=3, allow_redirects=False) as response:
                    if response.status == 200:
                        return {
                            'url': url,
                            'path': path,
                            'status': response.status,
                            'type': 'exposed'
                        }
                    elif response.status == 403:
                        return {
                            'url': url,
                            'path': path,
                            'status': response.status,
                            'type': 'forbidden'
                        }
            except:
                pass
            return None
        
        # Check all paths
        tasks = [check_path(path) for path in self.common_paths]
        path_results = await asyncio.gather(*tasks)
        
        for result in path_results:
            if result:
                if 'git' in result['path'] or 'env' in result['path'] or 'config' in result['path']:
                    results['issues'].append({
                        'type': 'critical_exposure',
                        'severity': 'critical',
                        'title': f'Critical file exposed: {result["path"]}',
                        'description': f'Sensitive file accessible at {result["url"]}',
                        'url': result['url']
                    })
                else:
                    results['exposed_paths'].append(result)
        
        # Check admin panels
        admin_tasks = [check_path(path) for path in self.admin_paths]
        admin_results = await asyncio.gather(*admin_tasks)
        
        for result in admin_results:
            if result and result['status'] == 200:
                results['admin_panels'].append(result)
                results['issues'].append({
                    'type': 'exposed_admin',
                    'severity': 'high',
                    'title': f'Admin panel exposed: {result["path"]}',
                    'description': f'Admin login page accessible without restrictions',
                    'url': result['url']
                })
        
        return results
