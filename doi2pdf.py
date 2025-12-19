import os
import time
import requests
from urllib.parse import urlparse, urlunparse
from selenium import webdriver
from selenium.webdriver.common.by import By

def convert_to_hku_proxy(url: str) -> str:
    """
    Convert a publisher URL into HKU library proxy format.
    Example:
    https://pubs.acs.org/doi/10.1021/acscatal.9b05338
    -> https://pubs-acs-org.eproxy.lib.hku.hk/doi/10.1021/acscatal.9b05338
    """
    parsed = urlparse(url)
    # Replace dots in the domain with dashes, then append HKU proxy suffix
    proxy_netloc = parsed.netloc.replace('.', '-') + ".eproxy.lib.hku.hk"
    proxied_url = urlunparse((parsed.scheme, proxy_netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
    return proxied_url


def doi_to_url(doi: str) -> tuple[str, str]:
    """
    Resolve a DOI into its publisher URL and return the publisher type.
    Example:
    '10.1021/acscatal.9b05338' ->
    ('https://pubs.acs.org/doi/10.1021/acscatal.9b05338', 'ACS')
    """
    resolver_url = f"https://doi.org/{doi}"
    try:
        response = requests.get(resolver_url, allow_redirects=True, timeout=10)
        response.raise_for_status()
        final_url = response.url
    except requests.HTTPError as e:
        # Even on error, response object may exist
        if e.response is not None:
            final_url = e.response.url
        else:
            return (f"Error resolving DOI {doi}: {e}", "Unknown")
    except requests.RequestException as e:
        return (f"Error resolving DOI {doi}: {e}", "Unknown")

    # Extract domain and map to publisher
    domain = urlparse(final_url).netloc
    publisher_map = {
        "pubs.acs.org": "ACS",
        "sciencedirect.com": "Elsevier",
        "link.springer.com": "Springer",
        "onlinelibrary.wiley.com": "Wiley",
        "tandfonline.com": "Taylor & Francis",
        "cambridge.org": "Cambridge University Press",
        "nature.com": "Nature Publishing Group",
        "ieee.org": "IEEE",
        "royalsocietypublishing.org": "Royal Society",
    }
    publisher = publisher_map.get(domain, "Unknown")

    return final_url, publisher


def _wait_for_page_load(driver, timeout=10):
    """Wait until document.readyState == 'complete' or timeout (seconds). Returns True if complete."""
    end = time.time() + timeout
    while time.time() < end:
        try:
            state = driver.execute_script("return document.readyState")
            if state == "complete":
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def process_dois(dois: list[str], driver_obj, wait_time: int = 10, proxy=None) -> dict:
    """
    Process a list of DOIs:
    - Resolve each DOI to a publisher URL and publisher via `doi_to_url`
    - Optionally convert the publisher URL using a proxy function
    - Perform publisher-specific actions (e.g., for ACS, navigate and click the PDF button)

    The `proxy` parameter may be:
    - None or 'hku' (default): use `convert_to_hku_proxy`
    - 'none': do not proxy, use the resolved URL directly
    - a callable: function that accepts (url: str) and returns a proxied URL (str)

    Behavior change: the very first page navigation will sleep 20s to allow the user to log in via the proxy; subsequent pages will wait for page load using `_wait_for_page_load`.

    Returns a dict mapping DOI -> info dict with keys: url, publisher, proxied_url, status, actions, error (if any).
    """
    results = {}

    local_driver = driver_obj
    first_visit = True

    for doi in dois:
        info: dict = {"doi": doi}
        url, publisher = doi_to_url(doi)
        info["url"] = url
        info["publisher"] = publisher

        if isinstance(url, str) and url.startswith("Error"):
            info["status"] = "resolve_failed"
            info["actions"] = []
            results[doi] = info
            continue

        # Determine proxied URL using the provided proxy parameter
        try:
            if proxy is None or proxy == 'hku':
                proxied = convert_to_hku_proxy(url)
            elif proxy == 'none':
                proxied = url
            elif callable(proxy):
                proxied = proxy(url)
            else:
                # Unknown proxy string: fall back to HKU proxy
                proxied = convert_to_hku_proxy(url)
        except Exception as e:
            info["status"] = "proxy_error"
            info["error"] = f"proxy function error: {e}"
            info["actions"] = []
            results[doi] = info
            continue

        info["proxied_url"] = proxied
        info["actions"] = []

        try:
            # Always navigate to the proxied URL so the user can login once, and the session persists for later pages.
            local_driver.get(proxied)

            if first_visit:
                # Give the user time to authenticate via the proxy (e.g., CAS login) on the first page
                time.sleep(20)
                first_visit = False
            else:
                # For later pages just wait for the page to load (not a fixed long sleep)
                _wait_for_page_load(local_driver, timeout=wait_time)

            # Publisher switch: implement ACS; add more branches as needed
            if publisher == "ACS":
                try:
                    pdf_button = local_driver.find_element(By.CLASS_NAME, "article__btn__secondary--pdf")
                    pdf_button.click()
                    info["actions"].append("clicked_pdf_button")
                    time.sleep(3)
                    info["status"] = "pdf_clicked"
                except Exception as e:
                    info["status"] = "click_pdf_failed"
                    info["error"] = str(e)
            elif publisher == "Elsevier":
                info["status"] = "no_action_for_publisher"
            else:
                info["status"] = "no_action_for_publisher"
        except Exception as e:
            info["status"] = "navigation_error"
            info["error"] = str(e)

        results[doi] = info

    return results


class DOI2PDFDownloader:
    """
    Simple DOI2PDFDownloader class that manages a queue of DOIs and a browser driver.

    Interfaces:
    - setup(download_path, proxy_method): configure download path and proxy style
    - add_dois(dois): add a DOI or list of DOIs to queue
    - start_sync(wait_time): synchronously process the queue and return results
    - start_async(): placeholder for future asynchronous implementation
    - close(): close the owned browser driver
    """
    def __init__(self, download_path=None, proxy_method='hku', headless=False):
        self._queue = []
        self.proxy_method = proxy_method
        self.headless = headless
        self.chrome_options = webdriver.ChromeOptions()
        self.prefs = {
            "plugins.always_open_pdf_externally": True,
            "download.default_directory": os.path.abspath("."),  #
            "download.prompt_for_download": False,
        }

        if download_path:
            self.prefs["download.default_directory"] = os.path.abspath(download_path)
        self.chrome_options.add_experimental_option("prefs", self.prefs)
        self._driver = webdriver.Chrome(options=self.chrome_options)

    def setup(self, download_path=None, proxy_method=None, headless=None):
        if download_path:
            self.prefs["download.default_directory"] = os.path.abspath(download_path)
        if proxy_method is not None:
            self.proxy_method = proxy_method
        if headless is not None:
            self.headless = headless
        self.chrome_options.add_experimental_option("prefs", self.prefs)
        self._driver = webdriver.Chrome(options=self.chrome_options)


    def add_dois(self, dois):
        if isinstance(dois, str):
            self._queue.append(dois)
        else:
            self._queue.extend(dois)

    def start_download_sync(self, wait_time=10):
        results = process_dois(self._queue, driver_obj=self._driver, wait_time=wait_time)
        self._queue = []
        return results

    def start_download_async(self):
        raise NotImplementedError("Asynchronous start is not implemented yet.")

    def close(self):
        if self._driver:
            try:
                self._driver.quit()
            except Exception:
                pass


# Example usage
if __name__ == "__main__":
    dl = DOI2PDFDownloader(download_path='.', proxy_method='hku')
    dl.add_dois(["10.1021/acscatal.9b05338", "10.1021/jacs.5c12544", "10.1021/acs.jpcc.3c04283"])
    results = dl.start_download_sync(wait_time=10)
    print(results)
    dl.close()
