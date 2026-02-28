"""
Advanced configuration system for  ssec-seo
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import os
import json

@dataclass
class ScanConfig:
    """Master configuration for scans"""
    
    # Crawler settings
    max_pages: int = 1000
    max_depth: int = 10
    concurrent_requests: int = 50
    request_timeout: int = 30
    crawl_delay: float = 0.1  # Seconds between requests
    respect_robots: bool = True
    follow_redirects: bool = True
    max_redirects: int = 5
    
    # Scope settings
    include_subdomains: bool = True
    exclude_patterns: List[str] = field(default_factory=lambda: [
        r'\.(jpg|jpeg|png|gif|bmp|svg|ico|css|js|woff|woff2|ttf|eot)$',
        r'logout',
        r'wp-admin',
    ])
    
    # Scanner settings
    check_exposed_data: bool = True
    check_dead_links: bool = True
    check_ssl_tls: bool = True
    check_headers: bool = True
    check_performance: bool = True
    check_seo_quality: bool = True
    check_content_quality: bool = True
    check_subdomains: bool = True
    check_redirect_chains: bool = True
    check_misconfigurations: bool = True
    check_technologies: bool = True
    
    # Analysis depth
    deep_content_analysis: bool = True
    extract_keywords: bool = True
    readability_analysis: bool = True
    sentiment_analysis: bool = False
    plagiarism_check: bool = False
    
    # Performance
    cache_responses: bool = True
    cache_ttl: int = 3600  # 1 hour
    use_session_reuse: bool = True
    max_memory_mb: int = 512
    
    # Reporting
    generate_html: bool = True
    generate_pdf: bool = True
    generate_json: bool = True
    generate_csv: bool = True
    include_charts: bool = True
    include_screenshots: bool = False
    detailed_mode: bool = True
    
    # Advanced
    use_stealth_mode: bool = True  # Avoid detection
    rotate_user_agents: bool = True
    use_proxy_rotation: bool = False
    proxy_list: List[str] = field(default_factory=list)
    
    @classmethod
    def from_file(cls, path: str) -> 'ScanConfig':
        """Load config from JSON file"""
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(**data)
    
    def to_file(self, path: str):
        """Save config to JSON file"""
        with open(path, 'w') as f:
            json.dump(self.__dict__, f, indent=2)
