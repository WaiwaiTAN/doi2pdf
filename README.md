# doi2pdf 📥

A small Python module to resolve DOIs, proxy publisher pages via HKU proxy (or a user-provided function), and perform publisher-specific actions (e.g., click ACS PDF button) using Selenium.

## Features ✅
- Resolve DOI -> publisher URL and detect publisher
- Optional HKU-proxy conversion or user-supplied proxy function
- Headless or interactive Chrome usage via Selenium
- `DOI2PDFDownloader` class with queue management and synchronous download

---

## Installation 🔧

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Make sure Chrome and a matching ChromeDriver are available on PATH.
   - This project was tested with **Chrome 143**; ensure your ChromeDriver matches your Chrome version.
   - Optionally use `webdriver-manager` in your own wrapper to auto-download drivers.

---

## Quick usage 💡

Synchronous example using the `DOI2PDFDownloader` class:

```python
from doi2pdf import DOI2PDFDownloader

# create downloader (defaults to HKU proxy behavior)
dl = DOI2PDFDownloader(download_path='.', proxy_method='hku')
# queue DOIs
dl.add_dois(["10.1021/acscatal.9b05338", "10.1021/acs.jpcc.3c04283"])
# start (first page will wait 20s for authentication, then pages wait for load)
results = dl.start_sync(wait_time=10)
print(results)
# close the browser
dl.close()
```

Direct call to `process_dois` (useful for custom driver/proxy functions):

```python
from doi2pdf import process_dois

# `driver` should be a Selenium webdriver instance
results = process_dois(["10.1021/acscatal.9b05338"], driver, wait_time=8, proxy='hku')

# or use a custom proxy callable
def my_proxy(url: str) -> str:
    return url.replace('https://', 'https://myproxy.example.com/')

results = process_dois(["10.1021/acscatal.9b05338"], driver, proxy=my_proxy)
```

---

## Notes & Caveats ⚠️
- The current implementation provides a synchronous `start_sync` method; asynchronous behavior is a TODO.
- The first navigation allows 20s for interactive login (e.g., institution CAS); subsequent navigations wait for the page to reach `document.readyState == 'complete'` (configurable via `wait_time`).
- Publisher-specific automation is implemented for ACS (clicks the PDF button). Add more branches in `process_dois` for other publishers.
- Running Selenium requires a compatible Chrome/Chromedriver installed; you can run headless by setting `headless=True` in `Downloader`.

---

## Contributing ✨
- Add tests for publisher behaviors
- Add Async start implementation
- Improve driver management (e.g., support for Firefox, remote drivers, or webdriver-manager integration)

---

If you'd like, I can add a LICENSE, GitHub Actions CI, or a small example script for publishing to GitHub—what would you prefer next? 🚀
