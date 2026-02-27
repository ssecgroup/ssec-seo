"""
Web crawler/spider for SEO analysis
"""
import asyncio
import aiohttp
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import Set, List, Dict, Optional
from dataclasses import dataclass, field
import time

@dataclass
class PageData:
    """Data collected from a single page"""
    url: str
    status_code: int
    title: str = ""
    meta_description: str = ""
    h1_tags: List[str] = field(default_factory=list)
    h2_tags: List[str] = field(default_factory=list)
    internal_links: Set[str] = field(default_factory=set)
    external_links: Set[str] = field(default_factory=set)
    broken_links: List[Dict] = field(default_factory=list)
    load_time: float = 0.0
    content_length: int = 0
    word_count: int = 0
    images_without_alt: int = 0
    has_robots_txt: bool = False
    has_sitemap: bool = False
    headers: Dict = field(default_factory=dict)

class SEOSpider:
    """Intelligent SEO crawler"""
    
    def __init__(self, start_url: str, max_pages: int = 100, concurrent: int = 10):
        self.start_url = start_url
        self.base_domain = urlparse(start_url).netloc
        self.max_pages = max_pages
        self.concurrent = concurrent
        self.visited: Set[str] = set()
        self.to_visit: asyncio.Queue = asyncio.Queue()
        self.results: List[PageData] = []
        self.session = None
        self.semaphore = asyncio.Semaphore(concurrent)
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    async def crawl(self) -> List[PageData]:
        """Start crawling from the start URL"""
        await self.to_visit.put(self.start_url)
        
        # Check robots.txt first
        await self._check_robots_txt()
        
        # Create worker tasks
        workers = [self._worker() for _ in range(self.concurrent)]
        await asyncio.gather(*workers)
        
        return self.results
    
    async def _worker(self):
        """Worker process to handle URLs"""
        while len(self.visited) < self.max_pages:
            try:
                url = await asyncio.wait_for(self.to_visit.get(), timeout=5)
            except asyncio.TimeoutError:
                break
                
            if url in self.visited:
                continue
                
            self.visited.add(url)
            
            async with self.semaphore:
                await self._process_url(url)
    
    async def _process_url(self, url: str):
        """Process a single URL"""
        start_time = time.time()
        
        try:
            async with self.session.get(url, timeout=10, ssl=False) as response:
                load_time = time.time() - start_time
                content = await response.text()
                
                # Parse the page
                soup = BeautifulSoup(content, 'html.parser')
                
                # Create page data
                page = PageData(
                    url=url,
                    status_code=response.status,
                    title=self._get_title(soup),
                    meta_description=self._get_meta_description(soup),
                    h1_tags=self._get_headings(soup, 'h1'),
                    h2_tags=self._get_headings(soup, 'h2'),
                    load_time=load_time,
                    content_length=len(content),
                    word_count=len(content.split()),
                    images_without_alt=self._count_images_without_alt(soup),
                    headers=dict(response.headers)
                )
                
                # Extract and queue links
                links = self._extract_links(soup, url)
                for link in links:
                    if self._should_crawl(link):
                        await self.to_visit.put(link)
                
                self.results.append(page)
                print(f"✅ Crawled: {url} ({load_time:.2f}s)")
                
        except Exception as e:
            print(f"❌ Error crawling {url}: {str(e)}")
    
    def _get_title(self, soup) -> str:
        """Extract page title"""
        title = soup.find('title')
        return title.text.strip() if title else ""
    
    def _get_meta_description(self, soup) -> str:
        """Extract meta description"""
        meta = soup.find('meta', attrs={'name': 'description'})
        return meta.get('content', '').strip() if meta else ""
    
    def _get_headings(self, soup, tag: str) -> List[str]:
        """Extract headings"""
        return [h.text.strip() for h in soup.find_all(tag)]
    
    def _count_images_without_alt(self, soup) -> int:
        """Count images missing alt text"""
        images = soup.find_all('img')
        return sum(1 for img in images if not img.get('alt'))
    
    def _extract_links(self, soup, base_url: str) -> Set[str]:
        """Extract all links from page"""
        links = set()
        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            if href and not href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                full_url = urljoin(base_url, href)
                links.add(full_url)
        return links
    
    def _should_crawl(self, url: str) -> bool:
        """Check if URL should be crawled"""
        # Only crawl same domain
        return urlparse(url).netloc == self.base_domain
    
    async def _check_robots_txt(self):
        """Check if robots.txt exists"""
        robots_url = urljoin(self.start_url, '/robots.txt')
        try:
            async with self.session.get(robots_url, timeout=5) as response:
                if response.status == 200:
                    print("✅ Found robots.txt")
        except:
            pass
