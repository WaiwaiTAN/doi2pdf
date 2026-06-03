# doi2pdf 📥

A Python library to resolve DOIs, proxy publisher pages via HKU proxy, and automate PDF downloads from academic publishers using Selenium.

## Installation

```bash
# Install from this directory
pip install .

# Or with optional webdriver-manager for automatic ChromeDriver
pip install ".[webdriver]"
```

## Requirements

- Python >=3.8
- selenium >=4.8.0
- requests >=2.28.0
- Chrome and matching ChromeDriver (tested with Chrome 143)
  - Optional: Install `webdriver-manager` extra to auto-download ChromeDriver

## Usage

### Using DOI2PDFDownloader (Recommended)

```python
from doi2pdf import DOI2PDFDownloader

# Create downloader (uses HKU proxy by default)
dl = DOI2PDFDownloader(download_path='.', proxy_method='hku')

# Add DOIs to queue
dl.add_dois([
    "10.1021/acscatal.9b05338",
    "10.1021/acs.jpcc.3c04283"
])

# Start browser and process DOIs
# First page waits 20s for login, subsequent pages wait for load
results = dl.start_download_sync(wait_time=10)

print(results)

# Close browser
dl.close()
```

### Using process_dois() function

```python
from selenium import webdriver
from doi2pdf import process_dois

# Set up your own Chrome driver
driver = webdriver.Chrome()

# Process DOIs with HKU proxy
results = process_dois(
    ["10.1021/acscatal.9b05338"],
    driver,
    wait_time=8,
    proxy='hku'
)

# Or use a custom proxy function
def my_proxy(url: str) -> str:
    return url.replace('https://', 'https://myproxy.example.com/')

results = process_dois(
    ["10.1021/acscatal.9b05338"],
    driver,
    proxy=my_proxy
)

driver.quit()
```

## API Reference

### DOI2PDFDownloader

```python
DOI2PDFDownloader(
    download_path=None,      # Where to save PDFs (default: current dir)
    proxy_method='hku',      # 'hku', 'none', or callable
    headless=False           # Run Chrome headless
)
```

**Methods:**
- `add_dois(dois)` - Add one or more DOIs to queue
- `start_download_sync(wait_time=10)` - Process queue synchronously
- `close()` - Close the browser

**Parameters:**
- `download_path` - Directory for PDF downloads
- `proxy_method` - How to proxy URLs:
  - `'hku'` (default) - Use HKU EZproxy
  - `'none'` - No proxy
  - `callable` - Your custom function: `fn(url) -> proxied_url`
- `wait_time` - Seconds to wait for page load (not first page)

### process_dois()

```python
process_dois(
    dois,                    # List of DOI strings
    driver_obj,             # Selenium WebDriver instance
    wait_time=10,           # Seconds to wait per page
    proxy=None              # 'hku', 'none', callable, or None
) -> dict                   # Results by DOI
```

## Features

- ✅ Resolve DOI → publisher URL and detect publisher
- ✅ Optional HKU-proxy conversion or custom proxy function
- ✅ Headless or interactive Chrome via Selenium
- ✅ Queue management with synchronous processing
- ✅ Publisher-specific automation (ACS PDF button, etc.)
- ✅ 20s initial login window for institutional CAS/Shibboleth

## Supported Publishers (with automation)

- **ACS** - Automatically clicks PDF download button
- **Elsevier** - Basic support (TODO: automated PDF download)
- **Others** - List supported but no special automation

## Notes

- First page navigation waits 20 seconds for user login via proxy (e.g., HKU CAS)
- Subsequent pages wait for `document.readyState == 'complete'` (configurable)
- You can run headless by setting `headless=True` in DOI2PDFDownloader
- For best results, ensure Chrome and ChromeDriver versions match

## Import from root doi2pdf package

The package also re-exports EZproxy utilities for convenience:

```python
from doi2pdf import hku_proxy_url, resolve_doi_to_domain, PUBLISHER_MAP

# Convert DOI to HKU proxy URL
url = hku_proxy_url("10.1038/nature12373")

# Resolve DOI to publisher domain
domain = resolve_doi_to_domain("10.1021/acscatal.9b05338")

# Get mapping of DOI prefixes to domains
print(PUBLISHER_MAP)
```

## License

MIT License

## Author

Tan Zheng <zhengtan@connect.hku.hk>
