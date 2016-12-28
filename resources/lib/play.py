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

import sys
import os
import re
import urllib2

import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin

import config
import utils
import classes
import comm

from pycaption import DFXPReader, SRTWriter


addon = xbmcaddon.Addon()

def play(url):
    try:
        params = utils.get_url(url)
        p = comm.get_program(params["program_id"])

        listitem=xbmcgui.ListItem(label=p.get_title(),
                                  iconImage=p.thumbnail,
                                  thumbnailImage=p.thumbnail,
                                  path=p.get_url())
        listitem.setInfo('video', p.get_xbmc_list_item())

        if hasattr(listitem, 'addStreamInfo'):
            listitem.addStreamInfo('audio', p.get_xbmc_audio_stream_info())
            listitem.addStreamInfo('video', p.get_xbmc_video_stream_info())
        
        if p.drm_key:
            import wvhelper
            
            if wvhelper.check_inputstream():
                listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
                listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
                listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
                listitem.setProperty('inputstream.adaptive.license_key', p.drm_key+'|Content-Type=application%2Fx-www-form-urlencoded|A{SSM}|')
            
            else:
                xbmcplugin.setResolvedUrl(_handle, True, xbmcgui.ListItem(path=None))
                return
            
        player = xbmc.Player()

        # Pull subtitles if available
        if addon.getSetting('subtitles_enabled') == "true":
            if p.subtitle:
                utils.log("Enabling subtitles: %s" % p.subtitle)
                profile = addon.getAddonInfo('profile')
                subfilename = xbmc.translatePath(os.path.join(profile, 'subtitle.srt'))
                profiledir = xbmc.translatePath(os.path.join(profile))
                if not os.path.isdir(profiledir):
                    os.makedirs(profiledir)

                dfxp_data = urllib2.urlopen(p.subtitle).read().decode('utf-8')
                if dfxp_data:
                    f = open(subfilename, 'w')
                    dfxp_subtitle = DFXPReader().read(dfxp_data)
                    srt_subtitle = SRTWriter().write(dfxp_subtitle)
                    srt_unicode = srt_subtitle.encode('utf-8')
                    f.write(srt_unicode)
                    f.close()

                if hasattr(listitem, 'setSubtitles'):
                    # This function only supported from Kodi v14+
                    listitem.setSubtitles([subfilename])

        # Play video
        utils.log("Attempting to play: %s" % p.get_title())
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=listitem)

        # Enable subtitles for XBMC v13
        if addon.getSetting('subtitles_enabled') == "true":
            if p.subtitle:
                if not hasattr(listitem, 'setSubtitles'):
                    while not player.isPlaying():
                        xbmc.sleep(100) # wait until video is being played
                        player.setSubtitles(subfilename)

    except:
        utils.handle_error("Unable to play video")
