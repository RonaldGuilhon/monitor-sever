"""Network utility functions"""

from urllib.parse import urlparse

def extract_port_from_url(url):
    """Extract port from URL, return default ports if not specified"""
    try:
        parsed = urlparse(url)
        if parsed.port:
            return parsed.port
        elif parsed.scheme == 'https':
            return 443
        elif parsed.scheme == 'http':
            return 80
        else:
            return None
    except Exception:
        return None

def extract_hostname_from_url(url):
    """Extract hostname from URL"""
    try:
        parsed = urlparse(url)
        return parsed.hostname
    except Exception:
        return None

def validate_url(url):
    """Validate if URL is properly formatted"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def format_url(host, port, scheme='http', path=''):
    """Format URL from components"""
    if not path.startswith('/'):
        path = '/' + path if path else ''
    return f"{scheme}://{host}:{port}{path}"