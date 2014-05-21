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

import os
import version

NAME = 'Plus7'
ADDON_ID = 'plugin.video.plus7'
VERSION = version.VERSION

try:
    uname = os.uname()
    os_string = ' (%s %s %s)' % (uname[0], uname[2], uname[4])
except AttributeError:
    os_string = ''

user_agent = '%s v%s for XBMC %s' % (NAME, VERSION, os_string)

api_url = 'https://y7mobile.query.yahoo.com/v1/yql'

# Took a LOT of effort to get this
oauth_consumer_key = 'dj0yJmk9QWJodDF5WDVnTGhwJmQ9WVdrOU1HODNiVXB0TnpnbWNHbzlNVGc0TWpnMk5UUTJNZy0tJnM9Y29uc3VtZXJzZWNyZXQmeD04Yw--'
oauth_consumer_secret = '0e4a80fc03b8ff1ed74a68a8dc583e77ff9e279b'
