#  ssec-seo - SEO Scanner by ssecgroup 

[![SEO Scanner](https://img.shields.io/badge/ssec--seo-Free%20SEO%20Scanner-667eea)](https://ssec-seo.vercel.app)
[![API Status](https://img.shields.io/badge/API-Live-success)](https://ssec-seo.vercel.app/api/debug)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-blue)](https://github.com/ssecgroup/ssec-seo/actions)
[![GitHub Pages](https://img.shields.io/badge/docs-github%20pages-blue)](https://ssecgroup.github.io/ssec-seo)
[![:hearts: Donate](https://img.shields.io/badge/:hearts: Donate-Ethereum-blue.svg)](#:hearts: Donate)
[![Edge Extension](https://img.shields.io/badge/Edge-Extension-blue)](https://microsoftedge.microsoft.com/addons/detail/ssec-seo-scanner/khenjefnlboennkponihcamfceccdlfi)
[![Firefox Add-on](https://img.shields.io/badge/Firefox-Add--on-orange)](https://addons.mozilla.org/addon/ssec-seo-scanner/)
[![Android](https://img.shields.io/badge/Android-APK-brightgreen)](https://github.com/ssecgroup/ssec-seo/releases/latest)
[![Windows](https://img.shields.io/badge/Windows-App-blue)](https://github.com/ssecgroup/ssec-seo/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/ssecgroup/ssec-seo/total)](https://github.com/ssecgroup/ssec-seo/releases)
[![Stars](https://img.shields.io/github/stars/ssecgroup/ssec-seo)](https://github.com/ssecgroup/ssec-seo/stargazers)

**The most advanced open-source SEO scanner - 100% FREE forever**  
*See what others miss. Find exposed data, subdomains, SSL issues, and more.*

---

##  Features

| Category | Capabilities |
|----------|--------------|
| **Deep Crawling** | 1000+ pages, redirect tracking, robots.txt respect |
| **Exposed Data** | Finds `.git`, `.env`, backups, config files, admin panels |
| **Subdomains** | Certificate logs + DNS brute force (1000+ subdomains) |
| **SSL/TLS** | Expiry alerts, protocol support, vulnerabilities |
| **Security** | HTTP headers, misconfigurations, directory listing |
| **Dead Links** | Full redirect chain analysis, broken link detection |
| **Reports** | Beautiful HTML with charts, one-click PDF export |
| **Free Cloud** | GitHub Actions integration - scan without installation | `CRITICAL` **Critical** | Exposed .git, .env, database backups, AWS keys | Severity | What We Detect |
|----------|----------------|
| `CRITICAL` **Critical** | Exposed .git, .env, database backups, AWS keys | Exposed .git, .env, database backups, AWS keys |
| `HIGH` **High** | Admin panels, phpinfo, directory listing, missing security headers | Admin panels, phpinfo, directory listing, missing security headers |
| `MEDIUM` **Medium** | SSL expiry <30 days, too many redirects, missing meta tags | SSL expiry <30 days, too many redirects, missing meta tags |
| `LOW` **Low** | Server info exposure, missing alt text, old file versions | Server info exposure, missing alt text, old file versions |

---

##  Installation on Different Platforms

### Linux / macOS
```bash
git clone https://github.com/ssecgroup/ssec-seo.git
cd ssec-seo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
ssec-seo --help
```

### Windows
```powershell
git clone https://github.com/ssecgroup/ssec-seo.git
cd ssec-seo
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
ssec-seo --help
```

### Docker
```bash
docker run --rm ssecgroup/ssec-seo scan https://example.com
```

---

##  Running Tests

```bash
# Unit tests
pytest tests/

# Test specific scanner
pytest tests/test_scanners/test_ssl_scanner.py

# Test with coverage
pytest --cov=ssec-seo tests/
```

---

##  Contributing

We welcome contributions! Here's how you can help:

1.  **Report bugs** - Open an issue
2.  **Suggest features** - Start a discussion
3.  **Fix issues** - Submit a PR
4.  **Improve docs** - Update README or wiki
5.  **Translate** - Add language support

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## ðŸ’– :hearts: Donate

ssec-seo is **completely free** and always will be.  
If you find it valuable, consider supporting development:

**Ethereum**: `0x8242f0f25c5445F7822e80d3C9615e57586c6639`

[![:hearts: Donate](https://img.shields.io/badge/:hearts: Donate-Ethereum-blue.svg)](https://etherscan.io/address/0x8242f0f25c5445F7822e80d3C9615e57586c6639)
[![Edge Extension](https://img.shields.io/badge/Edge-Extension-blue)](https://microsoftedge.microsoft.com/addons/detail/ssec-seo-scanner/khenjefnlboennkponihcamfceccdlfi)
[![Firefox Add-on](https://img.shields.io/badge/Firefox-Add--on-orange)](https://addons.mozilla.org/addon/ssec-seo-scanner/)
[![Android](https://img.shields.io/badge/Android-APK-brightgreen)](https://github.com/ssecgroup/ssec-seo/releases/latest)
[![Windows](https://img.shields.io/badge/Windows-App-blue)](https://github.com/ssecgroup/ssec-seo/releases/latest)

Your donations help:
-  Add new features
-  Fix bugs faster
-  Improve documentation
-  Keep free cloud scanning alive

---

##  Roadmap

- [x] Core crawling engine
- [x] SSL/TLS scanning
- [x] Subdomain discovery
- [x] Exposed data detection
- [x] Beautiful HTML reports
- [ ] Historical tracking
- [ ] Competitor analysis
- [ ] WordPress plugin
- [x] Browser extension ✅ **NOW LIVE!**
- [x] Android App ✅\n- [x] Windows App ✅\n- [ ] iOS App\n- [ ] API marketplace

---

##  License

MIT License - use it anywhere!  
Copyright (c) 2026 [ssecgroup](https://github.com/ssecgroup)

---

## â­ :star: Support Us

If you like ssec-seo:
- â­ :star: Star this repository
- ðŸ¦ Share on Twitter
- ðŸ‘¥ Tell your friends
- ðŸ’– :hearts: Donate to support development

---

**Made with :heart: by [ssecgroup](https://github.com/ssecgroup)**  
*Open source. Always free. Forever.*



