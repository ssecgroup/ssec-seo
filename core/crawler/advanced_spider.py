"""
Advanced web crawler with comprehensive features - FIXED VERSION
"""
import asyncio
import aiohttp
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
import random
from typing import Set, List, Dict, Optional, Tuple
from datetime import datetime
import time

class AdvancedSEOSpider:
    """
    Enterprise-grade SEO crawler with advanced features
    """
    
    def __init__(self, config):
        self.config = config
        self.base_domain = None
        self.visited = set()
        self.to_visit = asyncio.Queue()
        self.results = []
        self.session = None
        self.semaphore = asyncio.Semaphore(config.concurrent_requests)
        self.user_agents = self._load_user_agents()
        self.stats = {}
        self.start_time = None
        self.broken_links = []
        
    def _load_user_agents(self):
        """Load rotating user agents"""
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        ]
    
    async def __aenter__(self):
        """Setup session"""
        connector = aiohttp.TCPConnector(
            limit=self.config.concurrent_requests,
            ssl=False
        )
        
        timeout = aiohttp.ClientTimeout(
            total=self.config.request_timeout,
            connect=10
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        
        return self
    
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    async def crawl(self, start_url: str) -> Dict:
        """Start comprehensive crawl"""
        self.start_time = time.time()
        self.base_domain = urlparse(start_url).netloc
        
        # Add start URL to queue
        await self.to_visit.put((start_url, 0))
        print(f" Starting crawl of {self.base_domain}")
        
        # Create workers
        workers = [self._worker() for _ in range(self.config.concurrent_requests)]
        await asyncio.gather(*workers)
        
        print(f" Crawl complete: {len(self.results)} pages")
        
        return {
            'pages': self.results,
            'stats': self.stats,
            'crawl_time': time.time() - self.start_time,
            'broken_links': self.broken_links,
        }
    
    async def _worker(self):
        """Worker process"""
        while len(self.visited) < self.config.max_pages:
            try:
                url, depth = await asyncio.wait_for(self.to_visit.get(), timeout=5)
            except asyncio.TimeoutError:
                break
            
            if url in self.visited or depth > self.config.max_depth:
                continue
            
            self.visited.add(url)
            
            async with self.semaphore:
                await self._process_url(url, depth)
    
    async def _process_url(self, url: str, depth: int):
        """Process single URL"""
        page_data = {
            'url': url,
            'depth': depth,
            'timestamp': datetime.now().isoformat(),
            'issues': [],
            'findings': []
        }
        
        try:
            start_time = time.time()
            
            # Make request
            async with self.session.get(url, ssl=False) as response:
                load_time = time.time() - start_time
                
                page_data['status_code'] = response.status
                page_data['load_time'] = load_time
                page_data['headers'] = dict(response.headers)
                
                # Read content and store HTML for tech detection
                content = await response.text()
                page_data['html'] = content[:50000]  # Store first 50KB for analysis
                
                # Parse HTML
                soup = BeautifulSoup(content, 'lxml')
                
                # Extract basic info
                page_data['title'] = self._get_title(soup)
                page_data['meta_description'] = self._get_meta_description(soup)
                
                # Extract links
                links = self._extract_links(soup, url)
                page_data['internal_links'] = links['internal']
                page_data['external_links'] = links['external']
                
                # Queue internal links for crawling
                if depth < self.config.max_depth:
                    for link in links['internal']:
                        if link not in self.visited:
                            await self.to_visit.put((link, depth + 1))
                
                # Count elements
                page_data['image_count'] = len(soup.find_all('img'))
                page_data['script_count'] = len(soup.find_all('script'))
                page_data['css_count'] = len(soup.find_all('link', rel='stylesheet'))
                
                # Check for issues
                if not page_data['title']:
                    page_data['issues'].append({
                        'type': 'missing_title',
                        'severity': 'critical',
                        'description': 'Page has no title tag'
                    })
                
                if not page_data['meta_description']:
                    page_data['issues'].append({
                        'type': 'missing_description',
                        'severity': 'high',
                        'description': 'Page has no meta description'
                    })
                
                self.results.append(page_data)
                print(f"✅ Crawled: {url} ({load_time:.2f}s) - Depth: {depth}")
                
        except Exception as e:
            print(f"❌ Error: {url} - {str(e)}")
    
    def _get_title(self, soup) -> str:
        """Extract page title"""
        title = soup.find('title')
        return title.text.strip() if title else ""
    
    def _get_meta_description(self, soup) -> str:
        """Extract meta description"""
        meta = soup.find('meta', attrs={'name': 'description'})
        return meta.get('content', '').strip() if meta else ""
    
    def _extract_links(self, soup, base_url: str) -> Dict:
        """Extract all links"""
        internal = set()
        external = set()
        base_domain = urlparse(base_url).netloc
        
        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
            
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            
            if parsed.netloc == base_domain:
                internal.add(full_url)
            else:
                external.add(full_url)
        
        return {
            'internal': list(internal)[:50],  # Limit per page
            'external': list(external)[:20]
        }
