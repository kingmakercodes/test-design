import os
from urllib.parse import urlparse

def validate_environment(required_vars):
    missing_vars= [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise RuntimeError(f'Missing required environment variables: {",".join(missing_vars)}')

def validate_base_url(base_url):
    parsed_url= urlparse(base_url)
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError('Invalid BASE_URL provided in environment variable!')

    return parsed_url.geturl()