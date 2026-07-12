"""HKU EZproxy URL helpers."""

from __future__ import annotations

import json
import re
from urllib import error, request
from urllib.parse import quote, urlparse

PUBLISHER_MAP: dict[str, str] = {
    "10.1021": "pubs.acs.org",
    "10.1007": "link.springer.com",
    "10.1038": "www.nature.com",
    "10.1002": "onlinelibrary.wiley.com",
    "10.1109": "ieeexplore.ieee.org",
    "10.1039": "pubs.rsc.org",
    "10.1103": "journals.aps.org",
}

DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)


def _normalise_doi(doi: str) -> str:
    """Accept a bare DOI as well as common doi.org and ``doi:`` forms."""
    value = doi.strip()
    value = re.sub(r"^doi:\s*", "", value, flags=re.IGNORECASE)
    parsed = urlparse(value)
    if parsed.hostname and parsed.hostname.lower() in {"doi.org", "dx.doi.org"}:
        value = parsed.path.lstrip("/")
    if not DOI_RE.fullmatch(value):
        raise ValueError(f"Invalid DOI: {doi}")
    return value


def _resolve_doi_target(doi: str) -> tuple[str | None, str | None]:
    """Return the hostname and path registered in the DOI Handle record."""
    doi = _normalise_doi(doi)
    url = f"https://doi.org/api/handles/{quote(doi, safe='/')}"
    req = request.Request(
        url,
        headers={
            "User-Agent": "doi2proxy/0.1.1 (mailto:zhengtan@connect.hku.hk)",
            "Accept": "application/json",
        },
    )
    try:
        with request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read())
    except (error.URLError, json.JSONDecodeError):
        return None, None

    if data.get("responseCode") != 1:
        return None, None
    for value in data.get("values", []):
        if value.get("type") != "URL":
            continue
        target = value.get("data", {}).get("value", "")
        parsed = urlparse(target)
        if parsed.hostname:
            path = parsed.path or "/"
            if parsed.query:
                path += f"?{parsed.query}"
            return parsed.hostname.lower(), path
    return None, None


def resolve_doi_to_domain(doi: str) -> str | None:
    """Resolve *doi* to its publisher hostname."""
    domain, _ = _resolve_doi_target(doi)
    return domain


def _proxy_host(domain: str) -> str:
    return domain.replace(".", "-") + ".eproxy.lib.hku.hk"


def hku_proxy_url(doi: str) -> str:
    """Convert a DOI into its publisher URL through HKU EZproxy."""
    doi = _normalise_doi(doi)

    # Nature article URLs do not use the otherwise common /doi/<DOI> form.
    if doi.startswith("10.1038"):
        suffix = doi.split("/", 1)[1]
        return f"https://{_proxy_host('www.nature.com')}/articles/{suffix}"

    for prefix, domain in PUBLISHER_MAP.items():
        if doi.startswith(prefix):
            return f"https://{_proxy_host(domain)}/doi/{doi}"

    # MDPI (10.3390) and Elsevier (10.1016) deliberately reach this resolver.
    # Their canonical article paths cannot be derived reliably from the DOI.
    domain, path = _resolve_doi_target(doi)
    if domain and path:
        return f"https://{_proxy_host(domain)}{path}"

    return f"https://eproxy.lib.hku.hk/login?url=https://doi.org/{doi}"
