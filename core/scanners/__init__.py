"""
SPYGLASS Scanners Module
"""
from .dead_links import DeadLinkScanner
from .exposed_data import ExposedDataScanner
from .http_headers import HTTPHeadersScanner
from .http_misconfig import HTTPMisconfigScanner
from .redirects import RedirectScanner
from .security import SecurityScanner
from .ssl_scanner import SSLScanner
from .subdomain_scanner import SubdomainScanner
from .tech_detection import TechnologyDetector

# For backward compatibility
from .ssl_tls import SSLScanner as SSLScannerAlias
from .subdomain_scan import SubdomainScanner as SubdomainScannerAlias

__all__ = [
    'DeadLinkScanner',
    'ExposedDataScanner',
    'HTTPHeadersScanner',
    'HTTPMisconfigScanner',
    'RedirectScanner',
    'SecurityScanner',
    'SSLScanner',
    'SubdomainScanner',
    'TechnologyDetector'
]
