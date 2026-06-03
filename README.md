# doi2pdf & doi2proxy 📥

A Python toolkit to resolve DOIs, convert to HKU EZproxy URLs, and automate PDF downloads from academic publishers.

## 📦 Two Independent Projects

This repository contains two complementary packages:

### 1. **`doi2proxy`** - CLI tool for DOI to EZproxy conversion
- **Install:** `uv tool install ./doi2proxy`
- **Use:** `doi2proxy url 10.1038/nature12373`
- **No dependencies** - lightweight CLI tool
- Commands:
  - `doi2proxy url <DOI>` - Convert DOI to HKU EZproxy URL
  - `doi2proxy resolve <DOI>` - Resolve DOI to publisher domain
  - `doi2proxy list` - List supported publishers

### 2. **`doi2pdf`** - Python library for PDF automation
- **Install:** `pip install ./doi2pdf`
- **Use:** Import in Python code for automated PDF downloads with Selenium
- **Requires:** selenium, requests (for PDF automation)
- Classes:
  - `DOI2PDFDownloader` - Queue management and browser automation
  - `process_dois()` - Process list of DOIs with custom proxy functions

---

## 🚀 Quick Start

### Using `doi2proxy` CLI
```bash
# Install as a tool
uv tool install ./doi2proxy

# Convert DOI to proxy URL
doi2proxy url 10.1126/science.adr3149
# Output: https://www-science-org.eproxy.lib.hku.hk/doi/10.1126/science.adr3149

# Resolve DOI to publisher
doi2proxy resolve 10.1021/acscatal.9b05338

# List all supported publishers
doi2proxy list
```

### Using `doi2pdf` library
```bash
# Install as library
pip install ./doi2pdf

# Use in Python code
from doi2pdf import DOI2PDFDownloader

dl = DOI2PDFDownloader(download_path='.', proxy_method='hku')
dl.add_dois(["10.1021/acscatal.9b05338"])
results = dl.start_download_sync(wait_time=10)
dl.close()
```

---

## 📋 Requirements

- Python >=3.8
- For `doi2proxy`: No additional dependencies
- For `doi2pdf`: 
  - selenium >=4.8.0
  - requests >=2.28.0
  - Chrome and ChromeDriver for automation

---

## 📁 Directory Structure

```
.
├── doi2proxy/          # CLI tool (uv tool install)
│   ├── src/doi2proxy/
│   │   ├── __init__.py
│   │   ├── cli.py          # CLI entry point
│   │   └── ezproxy.py      # HKU EZproxy helper
│   ├── pyproject.toml
│   └── README.md
│
└── doi2pdf/            # PDF library (pip install)
    ├── src/doi2pdf/
    │   ├── __init__.py
    │   ├── downloader.py    # DOI2PDFDownloader class
    │   ├── elsevier.py      # Elsevier-specific automation
    │   └── _ezproxy.py      # Internal EZproxy helper
    ├── pyproject.toml
    └── README.md
```

---

## 📝 See Also

- `doi2proxy/README.md` - CLI tool documentation
- `doi2pdf/README.md` - Library documentation

---

## 📄 License

MIT License - see LICENSE file for details.

## 📧 Author

Tan Zheng <zhengtan@connect.hku.hk>
