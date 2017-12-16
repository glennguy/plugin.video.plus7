import threading
import socket
from SocketServer import TCPServer
from xbmc import Monitor
import xbmcaddon

from aussieaddonscommon import utils

from resources.lib.ThumbRequestHandler import ThumbRequestHandler

ADDON = xbmcaddon.Addon()

# server defaults
TCPServer.allow_reuse_address = True

def select_unused_port():
    """
    Helper function to select an unused port on the host machine
    :return: int - Free port
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 0))
    _, port = sock.getsockname()
    sock.close()
    return port


thumb_req_port = select_unused_port()    
ADDON.setSetting('thumbmail_port', str(thumb_req_port))
    
thumb_req_server = TCPServer(('127.0.0.1', thumb_req_port), ThumbRequestHandler)
thumb_req_server.server_activate()
thumb_req_server.timeout = 1
utils.log('Started 7Plus Thumbnail HTTP server on port {0}'
          .format(thumb_req_port))

if __name__ == '__main__':
    mon = Monitor()

    # start thread for thumbnail HTTP service
    thumb_req_thread = threading.Thread(target=thumb_req_server.serve_forever)
    thumb_req_thread.daemon = True
    thumb_req_thread.start()

    # kill the services if kodi monitor tells us to
    while not mon.abortRequested():
        if mon.waitForAbort(5):
            thumb_req_server.shutdown()
            break

    # Netflix service shutdown sequence
    thumb_req_server.server_close()
    thumb_req_server.socket.close()
    thumb_req_server.shutdown()
    utils.log('Stopped 7Plus Thumbnail HTTP server')
