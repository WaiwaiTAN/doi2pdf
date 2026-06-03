"""doi2pdf - Resolve DOIs and download PDFs with publisher-specific automation."""

from .downloader import DOI2PDFDownloader, process_dois
from ._ezproxy import hku_proxy_url, resolve_doi_to_domain, PUBLISHER_MAP

__all__ = ["DOI2PDFDownloader", "process_dois", "hku_proxy_url", "resolve_doi_to_domain", "PUBLISHER_MAP"]

