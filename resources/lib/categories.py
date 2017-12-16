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

import classes
import comm
import sys
import xbmcgui
import xbmcplugin

from aussieaddonscommon import utils


def make_categories_list():
    utils.log('Showing category list')
    try:
        categories_list = comm.get_categories()
        categories_list.sort()
        categories_list.insert(0, classes.Category(title='Live TV'))
        categories_list.append(classes.Category(title='Settings'))

        for c in categories_list:
            url = '{0}?action=list_categories&{1}'.format(sys.argv[0], c.make_kodi_url())
            listitem = xbmcgui.ListItem(label=c.title,
                                        iconImage=c.get_thumb(),
                                        thumbnailImage=c.get_thumb())

            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=True)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
    except Exception:
        utils.handle_error("Unable to show category listing")
