# Installation Guide 📦

This project contains two independent packages:

## 1. doi2proxy - CLI Tool (uv tool install)

A lightweight command-line tool to convert DOIs to HKU EZproxy URLs.

### Installation
```bash
# Install with uv tool
uv tool install ./doi2proxy

# Or install to a virtual environment
pip install ./doi2proxy
```

### Usage
```bash
# Convert DOI to HKU EZproxy URL
doi2proxy url 10.1038/nature12373
# Output: https://www-nature-com.eproxy.lib.hku.hk/doi/10.1038/nature12373

# Resolve DOI (with dynamic resolution)
doi2proxy resolve 10.1021/acscatal.9b05338

# List all supported publishers
doi2proxy list
```

### Features
- ✅ No dependencies - lightweight
- ✅ Works with `uv tool install`
- ✅ Can also be used as Python module

---

## 2. doi2pdf - PDF Library (pip install)

A Python library for automated PDF downloads from academic publishers using Selenium.

### Installation
```bash
# Install the library
pip install ./doi2pdf

# Or with optional webdriver-manager
pip install "./doi2pdf[webdriver]"
```

### Usage
```python
from doi2pdf import DOI2PDFDownloader

# Create downloader
dl = DOI2PDFDownloader(download_path='.', proxy_method='hku')

# Add DOIs to queue
dl.add_dois(["10.1021/acscatal.9b05338", "10.1021/acs.jpcc.3c04283"])

# Start processing
results = dl.start_download_sync(wait_time=10)

# Close browser
dl.close()
```

### Features
- ✅ Resolve DOI → publisher URL
- ✅ HKU EZproxy conversion
- ✅ Publisher-specific automation (ACS, Elsevier, etc.)
- ✅ Requires: selenium, requests, Chrome + ChromeDriver

---

## Project Structure

```
.
├── README.md                    # Overview
├── INSTALLATION_GUIDE.md        # This file
│
├── doi2proxy/                   # CLI tool project
│   ├── README.md               # CLI documentation
│   ├── pyproject.toml
│   └── src/doi2proxy/
│       ├── __init__.py
│       ├── cli.py              # Entry point
│       └── ezproxy.py          # EZproxy helper
│
└── doi2pdf/                     # PDF library project
    ├── README.md               # Library documentation
    ├── pyproject.toml
    └── src/doi2pdf/
        ├── __init__.py
        ├── downloader.py       # DOI2PDFDownloader class
        ├── elsevier.py         # Elsevier-specific code
        └── _ezproxy.py         # Internal EZproxy helper
```

---

## Quick Test

### Test doi2proxy
```bash
# Install in virtual environment
cd doi2proxy
uv venv
source .venv/bin/activate
uv pip install -e .

# Test commands
doi2proxy url 10.1038/nature12373
doi2proxy list
```

### Test doi2pdf
```bash
# Install in virtual environment
cd ../doi2pdf
uv venv
source .venv/bin/activate
uv pip install -e .

# Test import
python -c "from doi2pdf import DOI2PDFDownloader; print('✓ Import successful')"
```

---

## Notes

- Both projects are **independent** and can be installed separately
- `doi2proxy` has **no dependencies** and is ideal for `uv tool install`
- `doi2pdf` requires Selenium and is ideal for `pip install`
- Both share EZproxy functionality (doi2pdf includes a copy as `_ezproxy.py`)

