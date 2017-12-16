import classes
import comm
import json
import os
import sys
import urllib2
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from aussieaddonscommon import utils

from pycaption import SRTWriter
from pycaption import WebVTTReader

ADDON = xbmcaddon.Addon()


def play(params):
    try:
        p = comm.get_program(params)
        # enable HD streams
        if ADDON.getSetting('hd_enabled') == 'true':
            if '&rule=sd-only' in p.url:
                p.url = p.url.replace('&rule=sd-only', '')
        listitem = xbmcgui.ListItem(label=p.get_title(),
                                    #iconImage=p.get_thumb,
                                    #thumbnailImage=p.get_thumb,
                                    path=p.get_url())
        listitem.setInfo('video', p.get_kodi_list_item())

        if hasattr(listitem, 'addStreamInfo'):
            listitem.addStreamInfo('audio', p.get_kodi_audio_stream_info())
            listitem.addStreamInfo('video', p.get_kodi_video_stream_info())

        if p.dash:
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
                xbmcplugin.setResolvedUrl(int(sys.argv[1]),
                                          True,
                                          xbmcgui.ListItem(path=None))
                return

        # Pull subtitles if available
        if p.subtitle:
            utils.log('Enabling subtitles: {0}'.format(p.subtitle))
            profile = ADDON.getAddonInfo('profile')
            subfilename = xbmc.translatePath(os.path.join(profile,
                                                          'subtitle.srt'))
            profiledir = xbmc.translatePath(os.path.join(profile))
            if not os.path.isdir(profiledir):
                os.makedirs(profiledir)

            webvtt_data = urllib2.urlopen(
                p.subtitle).read().decode('utf-8')
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