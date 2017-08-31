import comm
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


def play(url):
    try:
        params = utils.get_url(url)
        p = comm.get_program(params['program_id'], 'live' in params)

        listitem = xbmcgui.ListItem(label=p.get_title(),
                                    iconImage=p.thumbnail,
                                    thumbnailImage=p.thumbnail,
                                    path=p.get_url())
        listitem.setInfo('video', p.get_kodi_list_item())

        if hasattr(listitem, 'addStreamInfo'):
            listitem.addStreamInfo('audio', p.get_kodi_audio_stream_info())
            listitem.addStreamInfo('video', p.get_kodi_video_stream_info())

        if p.drm_key:
            try:
                import drmhelper
            except ImportError:
                utils.log("Failed to import drmhelper")
                utils.dialog_message('This program is encrypted with DRM and '
                                     'DRM Helper not installed. For more '
                                     'information, please visit: '
                                     'http://aussieaddons.com/drm')
                return

            if drmhelper.check_inputstream():
                listitem.setProperty('inputstreamaddon',
                                     'inputstream.adaptive')
                listitem.setProperty('inputstream.adaptive.manifest_type',
                                     'mpd')
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

        player = xbmc.Player()

        # Pull subtitles if available
        if p.subtitle:
            utils.log("Enabling subtitles: %s" % p.subtitle)
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
        utils.log("Attempting to play: {0} : {1}".format(p.get_title(),
                                                         p.get_url()))
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=listitem)

    except Exception:
        utils.handle_error("Unable to play video")
