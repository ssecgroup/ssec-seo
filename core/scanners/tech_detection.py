"""
Technology stack detection - FIXED VERSION
"""
import re
from typing import Dict, List
from bs4 import BeautifulSoup

class TechnologyDetector:
    """Detect technologies used on websites"""
    
    def __init__(self):
        self.cms_patterns = {
            'WordPress': [
                r'wp-content',
                r'wp-includes',
                r'wp-json',
                r'wordpress',
                r'xmlrpc\.php'
            ],
            'Drupal': [
                r'drupal',
                r'sites/all',
                r'Drupal\.js'
            ],
            'Joomla': [
                r'joomla',
                r'com_content',
                r'option=com_'
            ],
            'Magento': [
                r'magento',
                r'skin/frontend',
                r'js/mage'
            ],
            'Shopify': [
                r'shopify',
                r'myshopify\.com',
                r'cdn\.shopify\.com'
            ]
        }
        
        self.js_frameworks = {
            'React': [
                r'react\.js',
                r'react-dom',
                r'React\.createElement',
                r'__REACT_DEVTOOLS_GLOBAL_HOOK__'
            ],
            'Vue.js': [
                r'vue\.js',
                r'__VUE__',
                r'v-bind',
                r'v-model'
            ],
            'Angular': [
                r'angular\.js',
                r'ng-app',
                r'ng-controller',
                r'ng-version'
            ],
            'jQuery': [
                r'jquery',
                r'\$\(document\)\.ready',
                r'jQuery\.fn'
            ],
            'Bootstrap': [
                r'bootstrap',
                r'col-md-',
                r'glyphicon'
            ]
        }
        
        self.analytics = {
            'Google Analytics': [
                r'google-analytics\.com',
                r'gtag',
                r'ga\('      # Fixed: removed extra backslash
            ],
            'Facebook Pixel': [
                r'facebook\.com/tr',
                r'fbq\('      # Fixed: removed extra backslash
            ],
            'Hotjar': [
                r'hotjar',
                r'hj\('       # Fixed: removed extra backslash
            ],
            'Mixpanel': [
                r'mixpanel',
                r'mixpanel\.init'
            ]
        }
        
        self.servers = {
            'Apache': [r'apache', r'httpd'],
            'Nginx': [r'nginx'],
            'IIS': [r'iis', r'microsoft-iis'],
            'Cloudflare': [r'cloudflare'],
            'AWS': [r'aws', r'amazon', r'Amazon']
        }
    
    def detect(self, headers: Dict, html: str, url: str) -> List[Dict]:
        """Detect technologies from headers and HTML"""
        technologies = []
        
        # Handle empty html
        if not html:
            html = ""
            
        try:
            soup = BeautifulSoup(html, 'lxml')
        except:
            soup = None
        
        # Check headers
        server = headers.get('server', '').lower()
        for tech, patterns in self.servers.items():
            for pattern in patterns:
                if pattern in server:
                    technologies.append({
                        'name': tech,
                        'category': 'server',
                        'confidence': 'high',
                        'evidence': f"Server header: {headers.get('server')}"
                    })
                    break
        
        # Check for Cloudflare
        if 'cf-ray' in headers or 'cf-cache-status' in headers:
            technologies.append({
                'name': 'Cloudflare',
                'category': 'cdn',
                'confidence': 'high',
                'evidence': 'Cloudflare headers present'
            })
        
        # Check CMS - with safe regex
        for cms, patterns in self.cms_patterns.items():
            for pattern in patterns:
                try:
                    if re.search(pattern, html, re.IGNORECASE):
                        technologies.append({
                            'name': cms,
                            'category': 'cms',
                            'confidence': 'medium',
                            'evidence': f"Pattern: {pattern}"
                        })
                        break
                except:
                    continue
        
        # Check JS frameworks - with safe regex
        html_lower = html.lower()
        for framework, patterns in self.js_frameworks.items():
            for pattern in patterns:
                try:
                    if pattern.lower() in html_lower or re.search(pattern, html, re.IGNORECASE):
                        technologies.append({
                            'name': framework,
                            'category': 'javascript',
                            'confidence': 'medium',
                            'evidence': f"Pattern: {pattern}"
                        })
                        break
                except:
                    continue
        
        # Check analytics - with safe regex
        for analytic, patterns in self.analytics.items():
            for pattern in patterns:
                try:
                    if re.search(pattern, html, re.IGNORECASE):
                        technologies.append({
                            'name': analytic,
                            'category': 'analytics',
                            'confidence': 'high',
                            'evidence': f"Pattern: {pattern}"
                        })
                        break
                except:
                    continue
        
        # Check meta tags for generator - safely
        if soup:
            try:
                generator = soup.find('meta', attrs={'name': 'generator'})
                if generator and generator.get('content'):
                    technologies.append({
                        'name': generator['content'],
                        'category': 'generator',
                        'confidence': 'high',
                        'evidence': f"Meta generator: {generator['content']}"
                    })
            except:
                pass
        
        # Remove duplicates
        unique_tech = []
        seen = set()
        for tech in technologies:
            key = f"{tech['name']}_{tech['category']}"
            if key not in seen:
                seen.add(key)
                unique_tech.append(tech)
        
        return unique_tech
