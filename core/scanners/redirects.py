"""
Redirect chain analyzer
"""
import aiohttp
from urllib.parse import urlparse
from typing import List, Dict

class RedirectScanner:
    """Analyze redirect chains for SEO issues"""
    
    async def scan(self, url: str, session: aiohttp.ClientSession) -> Dict:
        """Follow and analyze redirect chain"""
        results = {
            'initial_url': url,
            'final_url': url,
            'redirect_count': 0,
            'redirect_chain': [],
            'issues': []
        }
        
        current_url = url
        visited = set()
        chain = []
        
        try:
            for i in range(10):  # Max 10 redirects
                if current_url in visited:
                    results['issues'].append({
                        'type': 'redirect_loop',
                        'severity': 'critical',
                        'description': f'Redirect loop detected at {current_url}'
                    })
                    break
                
                visited.add(current_url)
                
                async with session.get(current_url, allow_redirects=False, ssl=False) as response:
                    chain.append({
                        'url': current_url,
                        'status': response.status,
                        'headers': dict(response.headers)
                    })
                    
                    if response.status in [301, 302, 303, 307, 308]:
                        location = response.headers.get('location')
                        if location:
                            # Check if redirect goes to different domain
                            old_domain = urlparse(current_url).netloc
                            new_url = location if location.startswith('http') else f"{urlparse(current_url).scheme}://{urlparse(current_url).netloc}{location}"
                            new_domain = urlparse(new_url).netloc
                            
                            if old_domain != new_domain:
                                results['issues'].append({
                                    'type': 'cross_domain_redirect',
                                    'severity': 'medium',
                                    'description': f'Redirects to different domain: {new_domain}',
                                    'url': current_url
                                })
                            
                            current_url = new_url
                        else:
                            break
                    else:
                        break
            
            results['final_url'] = current_url
            results['redirect_count'] = len(chain) - 1
            results['redirect_chain'] = chain
            
            # Check for too many redirects
            if results['redirect_count'] > 3:
                results['issues'].append({
                    'type': 'too_many_redirects',
                    'severity': 'medium',
                    'description': f'{results["redirect_count"]} redirects - bad for SEO',
                    'url': url
                })
            
            # Check for temporary redirects on important pages
            for redirect in chain[:-1]:
                if redirect['status'] == 302:
                    results['issues'].append({
                        'type': 'temporary_redirect',
                        'severity': 'low',
                        'description': 'Uses temporary redirect (302) - consider 301 for SEO',
                        'url': redirect['url']
                    })
                    
        except Exception as e:
            results['error'] = str(e)
        
        return results
