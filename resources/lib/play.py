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
import os	#need to write temp subtitle
import re	#need regular expression to read subtitle file
import urllib2	#need to fetch the subtitle

import xbmc
import xbmcgui
import xbmcaddon	#need to get addon info/profile

import config
import utils
import classes
import comm

def play(url):
    try:
        params = utils.get_url(url)
        p = comm.get_program(params["program_id"])

        listitem=xbmcgui.ListItem(label=p.get_title(), iconImage=p.thumbnail, thumbnailImage=p.thumbnail)
        listitem.setInfo('video', p.get_xbmc_list_item())

        if hasattr(listitem, 'addStreamInfo'):
            listitem.addStreamInfo('audio', p.get_xbmc_audio_stream_info())
            listitem.addStreamInfo('video', p.get_xbmc_video_stream_info())

        #get addon profile/path to create a temporary .srt file
	addon = xbmcaddon.Addon()
        profile = addon.getAddonInfo('profile')
        subfile = xbmc.translatePath(os.path.join(profile, 'temp.srt'))
        prodir  = xbmc.translatePath(os.path.join(profile))
        if not os.path.isdir(prodir):
            os.makedirs(prodir)

        #fetch the subtitle and convert to srt
	pg = urllib2.urlopen(p.subtitles).read()
        if pg != "":
            ofile = open(subfile, 'w+')
            captions = re.compile('<p begin="(.+?)" end="(.+?)">(.+?)</p>').findall(pg)
            idx = 1
            for cstart, cend, caption in captions:
                cstart = cstart.replace('.',',')
                cend   = cend.replace('.',',').split('"',1)[0]
                caption = caption.replace('<br/>','\n').replace('&gt;','>')
                ofile.write( '%s\n%s --> %s\n%s\n\n' % (idx, cstart, cend, caption))
                idx += 1
            ofile.close()
    
    	#tell the player to read the subtitle
	listitem.setSubtitles(['special://temp/temp.srt', subfile])
        
	utils.log("Attempting to play: %s" % p.get_title())
        xbmc.Player().play(p.get_url(), listitem)
    except:
        utils.handle_error("Unable to play video")
