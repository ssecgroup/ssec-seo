"""
Advanced subdomain discovery and analysis
"""
import asyncio
import aiohttp
import dns.resolver
import dns.reversename
from urllib.parse import urlparse
import json
import socket

class SubdomainScanner:
    """Discover and analyze subdomains"""
    
    def __init__(self):
        self.common_subdomains = [
            'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp',
            'pop', 'ns1', 'webdisk', 'ns2', 'cpanel', 'whm',
            'autodiscover', 'autoconfig', 'm', 'imap', 'test',
            'ns', 'blog', 'news', 'demo', 'stage', 'staging',
            'dev', 'development', 'prod', 'production', 'api',
            'app', 'admin', 'administrator', 'cms', 'portal',
            'secure', 'vpn', 'remote', 'exchange', 'owa',
            'docs', 'help', 'support', 'status', 'cdn',
            'cloud', 'assets', 'static', 'media', 'images',
            'img', 'css', 'js', 'download', 'downloads',
            'files', 'file', 'uploads', 'public', 'private',
            'backup', 'backups', 'old', 'new', 'beta',
            'alpha', 'test', 'testing', 'staging', 'preprod',
            'qa', 'quality', 'uat', 'demo', 'sandbox',
            'shop', 'store', 'cart', 'checkout', 'payment',
            'pay', 'billing', 'invoice', 'account', 'accounts',
            'profile', 'user', 'users', 'member', 'members',
            'login', 'signin', 'logout', 'signup', 'register',
            'auth', 'oauth', 'sso', 'identity', 'openid',
            'mobile', 'mob', 'mobi', 'tablet', 'iphone',
            'android', 'ios', 'ipad', 'app', 'apps',
            'api', 'rest', 'graphql', 'soap', 'xmlrpc',
            'ws', 'websocket', 'socket', 'stream', 'live',
            'video', 'audio', 'media', 'streaming', 'vod',
            'tv', 'radio', 'music', 'podcast', 'channel',
            'forum', 'community', 'group', 'groups', 'social',
            'chat', 'talk', 'message', 'messages', 'conversation',
            'webmail', 'email', 'mailer', 'smtp', 'imap',
            'pop3', 'pop', 'exchange', 'outlook', 'office',
            'calendar', 'cal', 'schedule', 'booking', 'reservation',
            'event', 'events', 'ticket', 'tickets', 'support',
            'help', 'helpdesk', 'desk', 'service', 'services',
            'customer', 'clients', 'client', 'partner', 'partners',
            'vendor', 'vendors', 'supplier', 'suppliers', 'distributor',
            'wholesale', 'retail', 'b2b', 'b2c', 'd2c',
            'corp', 'corporate', 'company', 'business', 'enterprise',
            'hr', 'human-resources', 'payroll', 'benefits', 'insurance',
            'legal', 'law', 'compliance', 'audit', 'risk',
            'security', 'secure', 'safety', 'protection', 'defense',
            'monitor', 'monitoring', 'alert', 'alerts', 'notification',
            'logs', 'log', 'logging', 'analytics', 'stat',
            'stats', 'statistics', 'metrics', 'measurement', 'insight',
            'report', 'reports', 'reporting', 'dashboard', 'board',
            'control', 'panel', 'manage', 'management', 'manager',
            'admin', 'administrator', 'super', 'master', 'root',
            'system', 'sys', 'server', 'servers', 'host',
            'node', 'nodes', 'cluster', 'cluster1', 'cluster2',
            'db', 'database', 'data', 'mysql', 'postgres',
            'mongodb', 'redis', 'elastic', 'search', 'elasticsearch',
            'cache', 'caching', 'redis', 'memcached', 'varnish',
            'proxy', 'reverse-proxy', 'load-balancer', 'lb', 'haproxy',
            'nginx', 'apache', 'httpd', 'iis', 'tomcat',
            'jenkins', 'git', 'github', 'gitlab', 'bitbucket',
            'svn', 'subversion', 'cvs', 'vcs', 'version',
            'ci', 'cd', 'continuous-integration', 'continuous-deployment', 'pipeline',
            'build', 'builder', 'compile', 'compiler', 'artifact',
            'docker', 'registry', 'container', 'k8s', 'kubernetes',
            'swarm', 'mesos', 'marathon', 'nomad', 'consul',
            'etcd', 'zookeeper', 'kafka', 'rabbitmq', 'activemq',
            'mq', 'queue', 'message-queue', 'pubsub', 'pub-sub',
            'spark', 'hadoop', 'hive', 'hbase', 'cassandra',
            'storm', 'flink', 'samza', 'beam', 'dataflow',
            'ml', 'ai', 'machine-learning', 'deep-learning', 'tensorflow',
            'pytorch', 'keras', 'caffe', 'mxnet', 'theano',
            'notebook', 'jupyter', 'lab', 'research', 'science',
            'graph', 'neo4j', 'janusgraph', 'dgraph', 'cayley',
            'blockchain', 'bitcoin', 'ethereum', 'crypto', 'wallet',
            'exchange', 'trade', 'trading', 'market', 'markets',
            'price', 'prices', 'chart', 'charts', 'graph'
        ]
        
        self.resolvers = [
            '8.8.8.8',  # Google
            '1.1.1.1',  # Cloudflare
            '9.9.9.9',  # Quad9
            '208.67.222.222',  # OpenDNS
        ]
    
    async def discover(self, domain: str) -> dict:
        """Discover subdomains using multiple techniques"""
        results = {
            'domain': domain,
            'subdomains': [],
            'active': [],
            'techniques': {},
            'total_found': 0
        }
        
        # Method 1: Certificate Transparency logs
        ct_subdomains = await self._scan_certificate_transparency(domain)
        results['subdomains'].extend(ct_subdomains)
        results['techniques']['certificate_transparency'] = len(ct_subdomains)
        
        # Method 2: DNS brute force
        dns_subdomains = await self._dns_bruteforce(domain)
        results['subdomains'].extend(dns_subdomains)
        results['techniques']['dns_bruteforce'] = len(dns_subdomains)
        
        # Method 3: Search engine scraping
        search_subdomains = await self._search_engine_scrape(domain)
        results['subdomains'].extend(search_subdomains)
        results['techniques']['search_engines'] = len(search_subdomains)
        
        # Remove duplicates
        results['subdomains'] = list(set(results['subdomains']))
        results['total_found'] = len(results['subdomains'])
        
        # Check which are active
        results['active'] = await self._check_active(results['subdomains'])
        
        return results
    
    async def _scan_certificate_transparency(self, domain: str) -> list:
        """Scan Certificate Transparency logs"""
        subdomains = set()
        
        # Use crt.sh (free, no API key)
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        for entry in data:
                            name = entry.get('name_value', '')
                            if name:
                                # Handle multiple names in one entry
                                for sub in name.split('\n'):
                                    if sub.endswith(f".{domain}") or sub == domain:
                                        subdomains.add(sub.strip())
        except Exception as e:
            print(f"CT log scan error: {e}")
        
        return list(subdomains)
    
    async def _dns_bruteforce(self, domain: str) -> list:
        """Brute force subdomains using DNS"""
        found = []
        resolver = dns.resolver.Resolver()
        resolver.nameservers = self.resolvers
        resolver.timeout = 2
        resolver.lifetime = 2
        
        async def check_subdomain(sub):
            try:
                full = f"{sub}.{domain}"
                answers = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: resolver.resolve(full, 'A')
                )
                if answers:
                    return full
            except:
                pass
            return None
        
        tasks = [check_subdomain(sub) for sub in self.common_subdomains]
        results = await asyncio.gather(*tasks)
        
        for result in results:
            if result:
                found.append(result)
                print(f"🌐 Found subdomain: {result}")
        
        return found
    
    async def _search_engine_scrape(self, domain: str) -> list:
        """Scrape search engines for subdomains"""
        subdomains = set()
        
        # Google scraping (basic)
        url = f"https://www.google.com/search?q=site:*.{domain}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as response:
                    if response.status == 200:
                        html = await response.text()
                        # Extract subdomains from results (simplified)
                        import re
                        pattern = r'https?://([a-zA-Z0-9.-]+)\.' + domain.replace('.', r'\.')
                        matches = re.findall(pattern, html)
                        subdomains.update(matches)
        except:
            pass
        
        return list(subdomains)
    
    async def _check_active(self, subdomains: list) -> list:
        """Check which subdomains are active"""
        active = []
        
        async def check(subdomain):
            for proto in ['https', 'http']:
                try:
                    url = f"{proto}://{subdomain}"
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, timeout=5, ssl=False) as response:
                            return {
                                'subdomain': subdomain,
                                'url': url,
                                'status': response.status,
                                'title': await self._get_title(response),
                                'accessible': True
                            }
                except:
                    continue
            return None
        
        tasks = [check(sub) for sub in subdomains[:50]]  # Limit checks
        results = await asyncio.gather(*tasks)
        
        for result in results:
            if result:
                active.append(result)
        
        return active
    
    async def _get_title(self, response) -> str:
        """Extract title from response"""
        try:
            text = await response.text()
            import re
            match = re.search(r'<title[^>]*>(.*?)</title>', text, re.IGNORECASE)
            return match.group(1).strip() if match else ''
        except:
            return ''
