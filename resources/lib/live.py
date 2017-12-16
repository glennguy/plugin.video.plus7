#
#   Plus7 XBMC Plugin
#   Copyright (C) 2014 Andy Botting
#
#
#   This plugin is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This plugin is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this plugin. If not, see <http://www.gnu.org/licenses/>.
#

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
            url = '{0}?action=list_programs&{1}'.format(sys.argv[0], c.make_kodi_url())
            # Add the program item to the list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=False)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except Exception:
        utils.handle_error("Unable to fetch live channel listing")
