import comm
import sys
import xbmcgui
import xbmcplugin

from aussieaddonscommon import utils


def make_series_list(params):
    utils.log('Showing series list')
    try:
        series_list = comm.get_series_list(params)
        series_list.sort()

        ok = True
        for s in series_list:
            url = '{0}?action=list_series&{1}'.format(sys.argv[0],
                                                      s.make_kodi_url())
            listitem = xbmcgui.ListItem(s.title,
                                        iconImage=s.get_thumb(),
                                        thumbnailImage=s.get_thumb())
            listitem.setInfo('video', {'plot': ''})

            # add the item to the media list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=True)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
    except Exception:
        utils.handle_error("Unable to fetch series listing")
