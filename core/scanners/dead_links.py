"""
Dead links and broken link checker
"""
import aiohttp
from urllib.parse import urljoin, urlparse
import asyncio
from typing import List, Dict, Set

class DeadLinkScanner:
    """Check for broken links on pages"""
    
    def __init__(self):
        self.broken_links = []
        self.checked_urls = set()
        
    async def scan(self, pages: List[Dict], session: aiohttp.ClientSession) -> List[Dict]:
        """Scan all pages for broken links"""
        print(f"🔍 Checking {sum(len(p.get('internal_links', [])) for p in pages)} links for broken status...")
        
        all_links = []
        link_sources = {}
        
        # Collect all unique links
        for page in pages:
            for link in page.get('internal_links', []) + page.get('external_links', []):
                if link not in self.checked_urls:
                    all_links.append(link)
                    if link not in link_sources:
                        link_sources[link] = []
                    link_sources[link].append(page['url'])
        
        # Check links in batches
        batch_size = 20
        broken = []
        
        for i in range(0, len(all_links), batch_size):
            batch = all_links[i:i+batch_size]
            tasks = [self._check_link(link, session) for link in batch]
            results = await asyncio.gather(*tasks)
            
            for link, is_broken, status in results:
                self.checked_urls.add(link)
                if is_broken:
                    broken.append({
                        'url': link,
                        'status': status,
                        'sources': link_sources.get(link, [])[:5],
                        'severity': 'high' if status == 404 else 'medium'
                    })
                    print(f"  ❌ Broken link: {link} ({status})")
        
        print(f"✅ Found {len(broken)} broken links")
        return broken
    
    async def _check_link(self, url: str, session: aiohttp.ClientSession) -> tuple:
        """Check if a link is broken"""
        try:
            async with session.head(url, timeout=5, allow_redirects=True, ssl=False) as response:
                if response.status >= 400:
                    return (url, True, response.status)
                return (url, False, response.status)
        except Exception as e:
            return (url, True, str(e))
