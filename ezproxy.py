"""HKU EZproxy helper for doi2pdf."""

from __future__ import annotations

import re
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

PUBLISHER_MAP: dict[str, str] = {
    "10.1021": "pubs.acs.org",
    "10.1016": "www.sciencedirect.com",
    "10.1007": "link.springer.com",
    "10.1038": "www.nature.com",
    "10.1002": "onlinelibrary.wiley.com",
    "10.1109": "ieeexplore.ieee.org",
    "10.1039": "pubs.rsc.org",
    "10.1103": "journals.aps.org",
}

DOI_PREFIX_RE = re.compile(r"^10\.\d{4,9}")


def resolve_doi_to_domain(doi: str) -> str | None:
    try:
        req = Request(f"https://doi.org/{doi}", method="HEAD")
        req.add_header("User-Agent", "Mozilla/5.0 (+doi2pdf)")
        with urlopen(req, timeout=5) as resp:
            loc = resp.headers.get("Location", "")
            from urllib.parse import urlparse
            return urlparse(loc).hostname
    except Exception:
        return None


def hku_proxy_url(doi: str) -> str:
    doi = doi.strip()

    for prefix, domain in PUBLISHER_MAP.items():
        if doi.startswith(prefix):
            proxied = domain.replace(".", "-") + ".eproxy.lib.hku.hk"
            return f"https://{proxied}/doi/{doi}"

    domain = resolve_doi_to_domain(doi)
    if domain:
        proxied = domain.replace(".", "-") + ".eproxy.lib.hku.hk"
        return f"https://{proxied}/doi/{doi}"

    return f"https://ezproxy.lib.hku.hk/login?url=https://doi.org/{doi}"