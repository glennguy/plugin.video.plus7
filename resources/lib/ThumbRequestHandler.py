import urlparse

from aussieaddonscommon import utils
from BaseHTTPServer import BaseHTTPRequestHandler


class ThumbRequestHandler(BaseHTTPRequestHandler):
    """Thumbnail HTTP request handler

    The 7Plus image service hosted with AWS Cloudfront does not respond
    typically to HTTP HEAD requests.

    Kodi will abort any attempt to load the image if the HEAD request
    returns a non-200 response.

    This HTTP request hander works around this issue by issuing a HTTP 200
    for any request that comes in, but issues a 302 redirect to the correct
    originating server for the HTTP GET.

    This is just enough to make thumbnails work correctly.
    """

    def do_GET(self):
        """Send a HTTP 302 for any HTTP GET request to SWM image server"""
        parsed_path = urlparse.urlparse(self.path)
        self.send_response(302)
        self.send_header('Location',
                         'https://imageproxy-cdn.swm.digital/image?{0}'
                         .format(parsed_path.query))
        self.end_headers()

    def do_HEAD(self):
        """Send a 200 on any HTTP HEAD request"""
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        utils.log('thumbnail request: %s' % self.requestline)
