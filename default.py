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
import sys
import xbmcaddon
import xbmcgui
# fix for python bug
import _strptime  # noqa: F401

import drmhelper
from aussieaddonscommon import utils

# Add our resources/lib to the python path
addon_dir = xbmcaddon.Addon().getAddonInfo('path')
sys.path.insert(0, os.path.join(addon_dir, 'resources', 'lib'))

import categories  # noqa: E402
import series  # noqa: E402
import programs  # noqa: E402
import play  # noqa: E402
import live  # noqa: E402

# Print our platform/version debugging information
utils.log_kodi_platform_version()


if __name__ == "__main__":
    params_str = sys.argv[2]
    params = utils.get_url(params_str)
    utils.log('Running with params: {0}'.format(params))
    if len(params) == 0:
        categories.make_categories_list()
    elif 'action' in params:
        action = params.get('action')
        if action == 'list_categories':
            if params['title'] == 'Live TV':
                live.make_live_list(params_str)
            elif params['title'] == 'Settings':
                xbmcaddon.Addon().openSettings()
            else:
                series.make_series_list(params)
        elif action == 'list_series':
            programs.make_programs_list(params)
        elif action == 'list_programs':
            play.play(params)
        elif action == 'sendreport':
            utils.user_report()
        elif action == 'reinstall_widevine_cdm':
            drmhelper.get_widevinecdm()
        elif action == 'reinstall_ssd_wv':
            drmhelper.get_ssd_wv()
        elif action == 'update_ia':
            addon = drmhelper.get_addon(drm=True)
            if not drmhelper.is_ia_current(addon, latest=True):
                if xbmcgui.Dialog().yesno(
                    'Upgrade?', ('Newer version of inputstream.adaptive '
                                 'available ({0}) - would you like to '
                                 'upgrade to this version?'.format(
                                    drmhelper.get_latest_ia_ver()))):
                    drmhelper.get_ia_direct(update=True, drm=True)
            else:
                ver = addon.getAddonInfo('version')
                utils.dialog_message('Up to date: Inputstream.adaptive '
                                     'version {0} installed and enabled.'
                                     ''.format(ver))
