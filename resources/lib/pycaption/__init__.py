from .base import CaptionConverter, Caption, CaptionSet, CaptionNode
from .dfxp import DFXPWriter, DFXPReader
from .srt import SRTReader, SRTWriter
from .exceptions import (
    CaptionReadError, CaptionReadNoCaptions, CaptionReadSyntaxError)


__all__ = [
    u'CaptionConverter', u'DFXPReader', u'DFXPWriter',
    u'SRTReader', u'SRTWriter',
    u'CaptionReadError', u'CaptionReadNoCaptions', u'CaptionReadSyntaxError',
    u'detect_format', u'Caption', u'CaptionSet', u'CaptionNode'
]

SUPPORTED_READERS = (DFXPReader, SRTReader)


def detect_format(caps):
    """
    Detect the format of the provided caption string.

    :returns: the reader class for the detected format.
    """
    for reader in SUPPORTED_READERS:
        if reader().detect(caps):
            return reader

    return None
