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
            url = '{0}?action=list_categories&{1}'.format(sys.argv[0],
                                                          c.make_kodi_url())
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
