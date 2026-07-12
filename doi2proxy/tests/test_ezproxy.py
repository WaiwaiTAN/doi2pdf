import json
from unittest.mock import patch

import pytest

from doi2proxy.ezproxy import hku_proxy_url, resolve_doi_to_domain


class Response:
    def __init__(self, target):
        self.payload = json.dumps(
            {
                "responseCode": 1,
                "values": [{"type": "URL", "data": {"value": target}}],
            }
        ).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self):
        return self.payload


@patch("doi2proxy.ezproxy.request.urlopen")
def test_mdpi_uses_registered_article_path(urlopen):
    urlopen.return_value = Response("https://www.mdpi.com/2073-4344/10/9/956")

    assert hku_proxy_url("10.3390/catal10090956") == (
        "https://www-mdpi-com.eproxy.lib.hku.hk/2073-4344/10/9/956"
    )


@patch("doi2proxy.ezproxy.request.urlopen")
def test_elsevier_uses_registered_article_path(urlopen):
    urlopen.return_value = Response(
        "https://www.sciencedirect.com/science/article/pii/S0926337320306386"
    )

    assert hku_proxy_url("10.1016/j.apcatb.2020.119416") == (
        "https://www-sciencedirect-com.eproxy.lib.hku.hk/"
        "science/article/pii/S0926337320306386"
    )


@patch("doi2proxy.ezproxy.request.urlopen")
def test_resolver_public_api_returns_domain_not_tuple(urlopen):
    urlopen.return_value = Response("https://www.mdpi.com/2073-4344/10/9/956")

    assert resolve_doi_to_domain("10.3390/catal10090956") == "www.mdpi.com"


def test_nature_article_path():
    assert hku_proxy_url("10.1038/nature12373") == (
        "https://www-nature-com.eproxy.lib.hku.hk/articles/nature12373"
    )


def test_accepts_doi_url():
    assert hku_proxy_url("https://doi.org/10.1021/example") == (
        "https://pubs-acs-org.eproxy.lib.hku.hk/doi/10.1021/example"
    )


def test_rejects_invalid_doi():
    with pytest.raises(ValueError, match="Invalid DOI"):
        hku_proxy_url("not-a-doi")
