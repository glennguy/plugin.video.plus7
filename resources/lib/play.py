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

import xbmc
import xbmcgui

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
    
        utils.log("Attempting to play: %s" % p.get_title())
        xbmc.Player().play(p.get_url(), listitem)
    except:
        utils.handle_error("Unable to play video")
