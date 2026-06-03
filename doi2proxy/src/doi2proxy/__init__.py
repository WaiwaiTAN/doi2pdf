"""doi2proxy - Convert DOI to HKU EZproxy URLs."""

from .ezproxy import hku_proxy_url, resolve_doi_to_domain, PUBLISHER_MAP

__all__ = ["hku_proxy_url", "resolve_doi_to_domain", "PUBLISHER_MAP"]
