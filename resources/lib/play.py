import comm
import os
import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from aussieaddonscommon import utils
from aussieaddonscommon import session

from pycaption import SRTWriter
from pycaption import WebVTTReader

ADDON = xbmcaddon.Addon()


def play(params):
    try:
        p = comm.get_program(params)
        # enable HD streams
        if ADDON.getSetting('hd_enabled') == 'true':
            if p.dash_url:
                if '&rule=sd-only' in p.dash_url:
                    p.dash_url = p.dash_url.replace('&rule=sd-only', '')
            if p.hls_url:
                if '&rule=sd-only' in p.hls_url:
                    p.hls_url = p.hls_url.replace('&rule=sd-only', '')
        listitem = xbmcgui.ListItem(label=p.get_title(),
                                    path=p.get_url())
        listitem.setInfo('video', p.get_kodi_list_item())

        if hasattr(listitem, 'addStreamInfo'):
            listitem.addStreamInfo('audio', p.get_kodi_audio_stream_info())
            listitem.addStreamInfo('video', p.get_kodi_video_stream_info())

        if (p.dash_preferred and p.dash_url) or not p.hls_url:
            import drmhelper
            drm = p.drm_key is not None

            if drmhelper.check_inputstream(drm=drm):
                listitem.setProperty('inputstreamaddon',
                                     'inputstream.adaptive')
                listitem.setProperty('inputstream.adaptive.manifest_type',
                                     'mpd')
                if drm:
                    listitem.setProperty('inputstream.adaptive.license_type',
                                         'com.widevine.alpha')
                    listitem.setProperty(
                        'inputstream.adaptive.license_key',
                        p.drm_key+'|Content-Type=application%2F'
                                  'x-www-form-urlencoded|A{SSM}|')
            else:
                if drm:
                    xbmcplugin.setResolvedUrl(int(sys.argv[1]),
                                              True,
                                              xbmcgui.ListItem(path=None))
                    return
                else:
                    pass  # let's try to play hls if available

        # Pull subtitles if available
        if p.subtitle:
            utils.log('Enabling subtitles: {0}'.format(p.subtitle))
            profile = ADDON.getAddonInfo('profile')
            subfilename = xbmc.translatePath(os.path.join(profile,
                                                          'subtitle.srt'))
            profiledir = xbmc.translatePath(os.path.join(profile))
            if not os.path.isdir(profiledir):
                os.makedirs(profiledir)

            webvtt_data = session.Session().get(
                p.subtitle).text
            if webvtt_data:
                with open(subfilename, 'w') as f:
                    webvtt_subtitle = WebVTTReader().read(webvtt_data)
                    srt_subtitle = SRTWriter().write(webvtt_subtitle)
                    srt_unicode = srt_subtitle.encode('utf-8')
                    f.write(srt_unicode)

            if hasattr(listitem, 'setSubtitles'):
                # This function only supported from Kodi v14+
                listitem.setSubtitles([subfilename])

        # Play video
        utils.log('Attempting to play: {0} : {1}'.format(p.get_title(),
                                                         p.get_url()))
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=listitem)

    except Exception:
        utils.handle_error('Unable to play video')
