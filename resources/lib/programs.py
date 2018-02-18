import comm
import sys
import xbmcgui
import xbmcplugin

from aussieaddonscommon import utils


def make_programs_list(params):
    try:
        programs = comm.get_programs_list(params)
        num_programs = len(programs)
        ok = True
        for p in programs:

            # Don't show any 'promo' shows,
            # they don't get returned by Brightcove
            if p.duration and p.duration < (5*60):
                utils.log("Skipping program {0} (duration {1} <5 mins)".format(
                    p.duration/60, p.get_list_title()))
                num_programs -= 1
                continue

            listitem = xbmcgui.ListItem(label=p.get_list_title(),
                                        iconImage=p.get_thumb(dummy_req=True),
                                        thumbnailImage=p.get_thumb())
            listitem.setInfo('video', p.get_kodi_list_item())
            listitem.setProperty('IsPlayable', 'true')

            if hasattr(listitem, 'addStreamInfo'):
                listitem.addStreamInfo('audio', p.get_kodi_audio_stream_info())
                listitem.addStreamInfo('video', p.get_kodi_video_stream_info())

            # Build the URL for the program, including the list_info
            url = '{0}?action=list_programs&{1}'.format(sys.argv[0],
                                                        p.make_kodi_url())

            # Add the program item to the list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=False,
                                             totalItems=num_programs)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except Exception:
        utils.handle_error("Unable to fetch program listing")
