import os
import time
import re
from urllib.parse import urlparse, urlunparse

import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# ==============================
# HKU eProxy URL convert
# ==============================
def convert_to_hku_proxy(url: str) -> str:
    parsed = urlparse(url)
    proxy_netloc = parsed.netloc.replace(".", "-") + ".eproxy.lib.hku.hk"
    return urlunparse((
        parsed.scheme,
        proxy_netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        parsed.fragment,
    ))


def wait_for_page_load(driver, timeout=25):
    end = time.time() + timeout
    while time.time() < end:
        try:
            if driver.execute_script("return document.readyState") == "complete":
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def wait_downloads_finish(download_dir: str, timeout: int = 30):
    """最后统一等：目录内没有 .crdownload"""
    t0 = time.time()
    while time.time() - t0 < timeout:
        crs = [f for f in os.listdir(download_dir) if f.endswith(".crdownload")]
        if not crs:
            return True
        time.sleep(0.5)
    raise TimeoutError("Download not finished within 30s")


# ==============================
# Read DOIs from Excel:
# first column, skip header row if present
# ==============================
def read_dois_from_excel(excel_path: str):
    df = pd.read_excel(excel_path, header=None)
    if df.shape[1] < 1:
        raise ValueError("Excel 至少需要一列 DOI（第一列）")

    col0 = df.iloc[:, 0].dropna().astype(str).str.strip().tolist()

    if col0 and col0[0].lower() in ("doi", "dois"):
        col0 = col0[1:]
    if len(col0) >= 2 and ("/" not in col0[0]) and ("/" in col0[1]):
        col0 = col0[1:]

    dois = [d for d in col0 if d and ("/" in d)]
    return dois


# ==============================
# Extract PII
# ==============================
def extract_pii(driver) -> str:
    url = driver.current_url
    m = re.search(r"/pii/([^/?#]+)", url)
    if m:
        return m.group(1)

    # meta citation_pii
    for sel in ["meta[name='citation_pii']", "meta[name='pii']", "meta[property='citation_pii']"]:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            val = (el.get_attribute("content") or "").strip()
            if val:
                return val
        except Exception:
            pass

    # 兜底：page_source 正则
    try:
        html = driver.page_source
        m2 = re.search(r'"pii"\s*:\s*"([^"]+)"', html)
        if m2:
            return m2.group(1)
    except Exception:
        pass

    raise RuntimeError(f"Cannot extract PII. current_url={url}")


def build_elsevier_pdf_url_from_pii(pii: str) -> str:
    return (
        "https://www-sciencedirect-com.eproxy.lib.hku.hk"
        f"/science/article/pii/{pii}/pdfft?isDTMRedir=true&download=true"
    )


def ensure_download_allowed(driver, download_dir: str):
    driver.execute_cdp_cmd("Page.setDownloadBehavior", {
        "behavior": "allow",
        "downloadPath": download_dir
    })


# ==============================
# Challenge / Verify handling
# ==============================
def is_challenge_page(driver) -> bool:
    u = (driver.current_url or "").lower()
    if "challenge" in u or "captcha" in u:
        return True
    try:
        html = driver.page_source.lower()
        # 常见：verify / challenge / noindex
        if ("verify" in html and "challenge" in html) or ("captcha" in html):
            return True
        if "noindex, nofollow" in html and "challenge" in html:
            return True
    except Exception:
        pass
    return False


def try_show_and_click_verify_checkbox(driver, timeout=15) -> bool:
    """
    尝试在主页面或 iframe 内找到并点击 Verify checkbox。
    成功返回 True，否则 False（需手动）。
    """
    wait = WebDriverWait(driver, timeout)

    # 主页面尝试
    selectors = [
        "label.cb-lb",
        "label.cb-lb input[type='checkbox']",
        "input[type='checkbox']",
        "span.cb-lb-t",  # Verify 文本
    ]

    driver.switch_to.default_content()

    for sel in selectors:
        try:
            el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            time.sleep(0.3)
            try:
                el.click()
            except Exception:
                driver.execute_script("arguments[0].click();", el)
            return True
        except TimeoutException:
            pass
        except Exception:
            pass

    # iframe 尝试
    driver.switch_to.default_content()
    iframes = driver.find_elements(By.TAG_NAME, "iframe")

    for iframe in iframes:
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(iframe)

            # iframe 内再试一次
            for sel in selectors:
                try:
                    el = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                    time.sleep(0.3)
                    try:
                        el.click()
                    except Exception:
                        driver.execute_script("arguments[0].click();", el)
                    driver.switch_to.default_content()
                    return True
                except Exception:
                    continue

        except Exception:
            continue

    driver.switch_to.default_content()
    return False


def handle_challenge_if_present(driver, manual_wait_sec=30, auto_try_timeout=15):
    """
    若检测到 challenge：
    - 先尝试自动点击 Verify
    - 失败则等待你手动完成
    """
    if not is_challenge_page(driver):
        return

    print(f"[ACTION] Challenge detected: {driver.current_url}")
    print("[ACTION] Trying to click Verify checkbox (if visible)...")

    clicked = False
    try:
        clicked = try_show_and_click_verify_checkbox(driver, timeout=auto_try_timeout)
    except Exception:
        clicked = False

    if clicked:
        print("[INFO] Verify clicked. Waiting for pass...")
        time.sleep(8)  # 给页面跳转/验证完成一点时间
        return

    print(f"[ACTION REQUIRED] Verify checkbox not found/clickable. Please complete verification manually ({manual_wait_sec}s)...")
    time.sleep(manual_wait_sec)


# ==============================
# Main
# ==============================
def main(excel_path="Publisher/elsevier.xlsx"):
    dois = read_dois_from_excel(excel_path)
    print(f"[INFO] Found {len(dois)} DOIs")
    if not dois:
        print("[WARN] No DOIs found. Exit.")
        return

    base_dir = os.path.abspath(os.path.dirname(__file__))
    download_dir = os.path.join(base_dir, "DownloadedPDF", "elsevier")
    os.makedirs(download_dir, exist_ok=True)
    print(f"[INFO] PDFs will be saved to: {download_dir}")

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("prefs", {
        "plugins.always_open_pdf_externally": True,
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "profile.default_content_setting_values.automatic_downloads": 1,
    })

    # 让浏览器更像人工使用，减少 challenge 概率（不绕过，只降低误判）
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--log-level=3")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 隐藏 navigator.webdriver（降低被误判概率）
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"}
        )

        ensure_download_allowed(driver, download_dir)

        # 1) 先打开第一个 DOI，让你手动登录一次
        first_url = convert_to_hku_proxy(f"https://doi.org/{dois[0]}")
        driver.get(first_url)
        wait_for_page_load(driver)

        print("[ACTION REQUIRED] 请手动完成 HKU / Elsevier 登录（一次即可，30 秒）")
        time.sleep(30)

        # 2) 强制触发一次 PDF challenge，并停住让你通过（你要求的）
        print("\n[STEP] Triggering a PDF download once to surface Verify page (if any)...")
        driver.get(convert_to_hku_proxy(f"https://doi.org/{dois[0]}"))
        wait_for_page_load(driver)
        handle_challenge_if_present(driver, manual_wait_sec=30)

        try:
            pii0 = extract_pii(driver)
            pdf0 = build_elsevier_pdf_url_from_pii(pii0)
            print(f"[INFO] Probe PII: {pii0}")
            print(f"[INFO] Probe PDF URL: {pdf0}")
            driver.get(pdf0)
            time.sleep(2)
            handle_challenge_if_present(driver, manual_wait_sec=45)
        except Exception as e:
            print(f"[WARN] Probe step failed (will continue anyway): {e}")

        # 3) 开始批量
        for i, doi in enumerate(dois, 1):
            print(f"\n[{i}/{len(dois)}] Processing DOI: {doi}")
            try:
                article_url = convert_to_hku_proxy(f"https://doi.org/{doi}")
                print(f"[INFO] Article URL: {article_url}")
                driver.get(article_url)
                wait_for_page_load(driver)
                handle_challenge_if_present(driver, manual_wait_sec=20)

                pii = extract_pii(driver)
                print(f"[INFO] PII: {pii}")

                pdf_url = build_elsevier_pdf_url_from_pii(pii)
                print(f"[INFO] Direct PDF URL: {pdf_url}")

                driver.get(pdf_url)
                time.sleep(2)
                handle_challenge_if_present(driver, manual_wait_sec=30)

                # 不逐篇等待下载完成
                time.sleep(1)

            except Exception as e:
                print(f"[FAILED] {doi}: {e}")

        # 4) 最后等 30 秒下载收尾
        print("\n[INFO] All DOIs processed. Waiting up to 30s for remaining downloads...")
        try:
            wait_downloads_finish(download_dir, timeout=30)
            print("[INFO] Downloads finished (no .crdownload).")
        except Exception as e:
            print(f"[WARN] Still downloading after 30s. Closing anyway. Details: {e}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main("Publisher/elsevier.xlsx")
