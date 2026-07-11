"""HKU EZproxy helper for doi2pdf."""

from __future__ import annotations

import re
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse

PUBLISHER_MAP: dict[str, str] = {
    "10.1021": "pubs.acs.org",
    "10.1007": "link.springer.com",
    "10.1038": "www.nature.com",
    "10.1002": "onlinelibrary.wiley.com",
    "10.1109": "ieeexplore.ieee.org",
    "10.1039": "pubs.rsc.org",
    "10.1103": "journals.aps.org",
}

DOI_PREFIX_RE = re.compile(r"^10\.\d{4,9}")


import json
from urllib import request, error
from urllib.parse import urlparse

def resolve_doi_to_domain(doi: str) -> tuple [str | None, str | None]:
    url = f"https://doi.org/api/handles/{doi}"
    req = request.Request(
        url,
        headers={
            "User-Agent": "doi2proxy/0.1 (mailto:zhengtan@connect.hku.hk)",
            "Accept": "application/json",
        },
    )
    try:
        with request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read())
            if data.get("responseCode") != 1:
                return None, None
            for v in data["values"]:
                if v["type"] == "URL":
                    parsed = urlparse(v["data"]["value"])
                    return parsed.hostname, parsed.path
    except error.URLError as e:
        print(f"网络错误：无法解析 DOI {doi}（{e.reason}）")
        raise
    except json.JSONDecodeError as e:
        print(f"格式错误：DOI {doi} 返回无效响应（{e.msg}）")
        raise
    except Exception as e:
        print(f"未知错误：{e}")
        raise

def hku_proxy_url(doi: str) -> str:
    doi = doi.strip()

    for prefix, domain in PUBLISHER_MAP.items():
        if doi.startswith(prefix):
            if domain != "nature.com":
                proxied = domain.replace(".", "-") + ".eproxy.lib.hku.hk"
                return f"https://{proxied}/doi/{doi}"
            else:
                proxied = domain.replace(".", "-") + ".eproxy.lib.hku.hk"
                suffix = doi.split("/", 1)[1]
                return f"https://{proxied}/articles/{suffix}"

    domain, path = resolve_doi_to_domain(doi)
    if domain:
        proxied = domain.replace(".", "-") + ".eproxy.lib.hku.hk"
        return f"https://{proxied}{path}"

    return f"https://eproxy.lib.hku.hk/login?url=https://doi.org/{doi}"