# doi2proxy 🔗

A lightweight CLI tool to convert DOI to HKU EZproxy URLs.

## Installation

```bash
# Install as a tool
cd doi2proxy
uv tool install --force .

# Or install to a virtual environment
pip install .
```

## Usage

```bash
# Convert DOI to HKU EZproxy URL
doi2proxy url 10.1038/nature12373
# Output: https://www-nature-com.eproxy.lib.hku.hk/articles/nature12373

# Resolve DOI to publisher domain
doi2proxy resolve 10.1021/acscatal.9b05338
# Output:
# Domain: pubs.acs.org
# Proxy URL: https://pubs-acs-org.eproxy.lib.hku.hk/doi/10.1021/acscatal.9b05338

# List all supported DOI prefixes and publishers
doi2proxy list
```

## Supported Publishers

The tool supports the following DOI prefixes and publishers:

```
10.1021      -> pubs.acs.org (ACS)
10.1007      -> link.springer.com (Springer)
10.1038      -> www.nature.com (Nature)
10.1002      -> onlinelibrary.wiley.com (Wiley)
10.1109      -> ieeexplore.ieee.org (IEEE)
10.1039      -> pubs.rsc.org (RSC)
10.1103      -> journals.aps.org (APS)
```

For DOIs not in the list, the tool will attempt to resolve the DOI to its actual publisher domain and create the proxy URL.
Elsevier (`10.1016`) and MDPI (`10.3390`) always use this dynamic resolution so
their publisher-specific article paths are preserved.

## Python API

If you install to a virtual environment, you can also use it as a Python module:

```python
from doi2proxy import hku_proxy_url, resolve_doi_to_domain, PUBLISHER_MAP

# Convert DOI to proxy URL
url = hku_proxy_url("10.1038/nature12373")
print(url)

# Resolve DOI to publisher domain
domain = resolve_doi_to_domain("10.1021/acscatal.9b05338")
print(domain)  # Output: pubs.acs.org

# Get all supported prefixes
print(PUBLISHER_MAP)
```

## Features

- ✅ No external dependencies - lightweight and fast
- ✅ Direct DOI to HKU EZproxy URL conversion
- ✅ Dynamic resolution of DOIs to publisher domains
- ✅ Easy CLI interface
- ✅ Usable as a Python module

## Requirements

- Python >=3.8
- No external dependencies

## License

MIT License

## Author

Tan Zheng <zhengtan@connect.hku.hk>
