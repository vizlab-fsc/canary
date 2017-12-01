import re
import requests
from dateutil import parser

# consider gifs images, but we don't handle them properly atm
IMG_RE = re.compile(r'\.(jpg|jpeg|gif|png)')
URL_RE = re.compile(r'(https?:\/)?(\/[\w\.\-]+)+\/?')


def image_urls(content):
    """extract urls, relative or absolute,
    that look like image urls"""
    urls = [url.group(0) for url in URL_RE.finditer(content)]
    return [url for url in urls if is_image(url)]


def query_image(url):
    """get some metadata about the remote image
    with a HEAD request"""
    resp = requests.head(url)
    last_modified = resp.headers.get('Last-Modified')
    if last_modified is not None:
        last_modified = parser.parse(last_modified).timestamp()
    return {
        'last_modified': last_modified,
        'content_type': resp.headers.get('Content-Type'),
        'content_length': resp.headers.get('Content-Length')
    }


def is_image(url):
    """check if a url is for an image.
    there is no foolproof way of doing this.
    in addition to checking for an image extension in the URL,
    we can also:
        - send a HEAD request and look at the Content-Type, but this can
        also be spoofed.
        - check for a magic number at the start of the file, but is also not
        a guarantee (<https://stackoverflow.com/a/676975/1097920>)
    """
    last = url.rsplit('/', 1)[-1]
    return IMG_RE.search(last) is not None
