#!/usr/bin/env python
"""CLI tool to convert DOI to HKU EZproxy URLs."""

from __future__ import annotations

import sys
import argparse
from .ezproxy import hku_proxy_url, resolve_doi_to_domain, PUBLISHER_MAP


def main() -> int:
    """Main entry point for the doi2proxy CLI tool."""
    parser = argparse.ArgumentParser(
        description="Convert DOI to HKU EZproxy URLs",
        prog="doi2proxy",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # url command: convert DOI to proxy URL
    url_parser = subparsers.add_parser(
        "url",
        help="Convert DOI to HKU EZproxy URL",
    )
    url_parser.add_argument(
        "doi",
        help="DOI to convert (e.g., 10.1038/nature12373)",
    )
    url_parser.add_argument(
        "--resolve",
        action="store_true",
        help="Resolve DOI to domain first",
    )
    
    # list command: list supported publishers
    list_parser = subparsers.add_parser(
        "list",
        help="List supported DOI prefixes and publishers",
    )
    
    # resolve command: resolve DOI to domain
    resolve_parser = subparsers.add_parser(
        "resolve",
        help="Resolve DOI to publisher domain",
    )
    resolve_parser.add_argument(
        "doi",
        help="DOI to resolve",
    )
    
    args = parser.parse_args()
    
    if args.command == "url":
        try:
            print(hku_proxy_url(args.doi))
            return 0
        except ValueError as exc:
            parser.error(str(exc))
    
    elif args.command == "list":
        print("Supported DOI prefixes and publishers:")
        print("-" * 60)
        for prefix, domain in PUBLISHER_MAP.items():
            print(f"{prefix:12} -> {domain}")
        return 0
    
    elif args.command == "resolve":
        try:
            domain = resolve_doi_to_domain(args.doi)
        except ValueError as exc:
            parser.error(str(exc))
        if domain:
            print(f"Domain: {domain}")
            # Also show the proxy URL
            url = hku_proxy_url(args.doi)
            print(f"Proxy URL: {url}")
            return 0
        else:
            print(f"Error: Could not resolve DOI {args.doi}", file=sys.stderr)
            return 1
    
    else:
        # Default: treat first argument as DOI if no command specified
        if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
            url = hku_proxy_url(sys.argv[1])
            print(url)
            return 0
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
