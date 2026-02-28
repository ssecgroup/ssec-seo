"""
ssec-seo API for Vercel
"""
import sys
import os
import json
import asyncio
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'ssec_seo'))
sys.path.insert(0, os.path.join(project_root, 'ssec_seo', 'core'))

try:
    from ssec_seo.core.ultimate_engine import UltimateSEOEngine
    from ssec_seo.core.config import ScanConfig
    HAS_ENGINE = True
except ImportError:
    try:
        from core.ultimate_engine import UltimateSEOEngine
        from core.config import ScanConfig
        HAS_ENGINE = True
    except ImportError as e:
        HAS_ENGINE = False
        import_error = str(e)

class handler(BaseHTTPRequestHandler):
    # ... (rest of handler code, same functionality)
