"""
🔍 SPYGLASS - Ultimate SEO Intelligence Platform
=================================================
The most advanced open-source SEO scanner ever built.

Features:
    • Complete website crawling with redirect tracking
    • Exposed data detection (.git, .env, backups, configs)
    • Subdomain discovery (certificate + DNS brute force)
    • SSL/TLS deep analysis with expiry monitoring
    • HTTP misconfiguration scanning
    • Security header analysis
    • Broken link detection
    • Technology stack detection
    • Beautiful HTML reports with interactive charts
    • PDF export with one click
    • Zero storage - reports generated on demand
    • MIT License - free forever

Usage:
    from spyglass import UltimateSEOEngine
    
    engine = UltimateSEOEngine()
    results = await engine.scan("https://example.com")
    engine.generate_report(results, "report.html")

CLI:
    spyglass scan https://example.com --auto-pdf
    spyglass quick https://example.com
    spyglass configure

Version: 0.1.0
License: MIT
Author: SPYGLASS Team
"""

__version__ = "0.1.0"
__author__ = "SPYGLASS Team"
__license__ = "MIT"

from spyglass.core.ultimate_engine import UltimateSEOEngine
from spyglass.core.config import ScanConfig

__all__ = ['UltimateSEOEngine', 'ScanConfig']
