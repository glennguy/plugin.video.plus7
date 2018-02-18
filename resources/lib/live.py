import comm
import sys
import xbmcaddon
import xbmcgui
import xbmcplugin

from aussieaddonscommon import utils

ADDON = xbmcaddon.Addon()


def make_live_list(url):
    try:
        channels = comm.get_live()
        if not channels:
            return

        ok = True
        for c in channels:

            listitem = xbmcgui.ListItem(label=c.get_list_title(),
                                        iconImage=c.get_thumb(dummy_req=True),
                                        thumbnailImage=c.get_thumb())
            listitem.setInfo('video', c.get_kodi_list_item())
            listitem.setProperty('IsPlayable', 'true')

            if hasattr(listitem, 'addStreamInfo'):
                listitem.addStreamInfo('audio', c.get_kodi_audio_stream_info())
                listitem.addStreamInfo('video', c.get_kodi_video_stream_info())

            # Build the URL for the program, including the list_info
            url = '{0}?action=list_programs&{1}'.format(sys.argv[0],
                                                        c.make_kodi_url())
            # Add the program item to the list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=False)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except Exception:
        utils.handle_error("Unable to fetch live channel listing")
