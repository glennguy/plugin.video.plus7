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
# flake8: noqa

import os

GITHUB_API_URL = 'https://api.github.com/repos/andybotting/xbmc-addon-plus7'
ISSUE_API_URL = GITHUB_API_URL + '/issues'
ISSUE_API_AUTH = 'eGJtY2JvdDo1OTQxNTJjMTBhZGFiNGRlN2M0YWZkZDYwZGQ5NDFkNWY4YmIzOGFj'
GIST_API_URL = 'https://api.github.com/gists'

ADDON_ID = 'plugin.video.plus7'

BRIGHTCOVE_M3U8_URL = 'http://c.brightcove.com/services/mobile/streaming/index/master.m3u8?videoId={0}'
BRIGHTCOVE_URL = 'https://edge.api.brightcove.com/playback/v1/accounts/{0}/videos/ref:{1}'
BRIGHTCOVE_ACCOUNT = {'2376984108001': 'BCpkADawqM23Rsu_vHPRKbrIicm3fvl2i33Q_d5KoWIQ1hAlTrmpbAbKyZWXQiZ_kbgJZ7DulFHPCscZmi-4Z_OsylPgPi3h8pnYWRwbKrstrrJt08gS8vYGG8aTRA87y6VhscthRz2ZUDTh',
                      '2376984109001': 'BCpkADawqM39TuhPMJu1xTBSj0v3v4zTIs9HKuYDYQlmmru1yrD5pzbFYN8OM_vu2PLXqAsUpZqgRL3hcUCUhARK1yYpo6Qt09r2p6A1xiTsiRFSLpsg7SV-aGHCuJ-a6O5k61OKwusrR2r1',
                      '4456740435001': 'BCpkADawqM3Ty0dStHsYNCVbgBXlEbdnC6vZah6As39gvutM2aTiYRIV5ZyJH4WTWRedIYgjbdrC7Hk6Mvdx3nddTtTCcJzP-KXbkprsB0PWpdx7NQyTfdU-RfWkfg_ymolet0kzHBf8taPO'}
API_VER = '1.0'

CONFIG_URL = 'https://config.swm.digital/android/1.0.json'
MARKET_URL = 'https://api.tvapi.com.au/v1/services/market/ip/?apikey=9ae52b994a46faea21d0c06288934025'
CONTENT_URL = 'https://component-cdn.swm.digital/content/'

shows_url = 'https://y7mobile.query.yahoo.com/v1/plus7/shows/public?device=play'
query_url = 'https://y7mobile.query.yahoo.com/v1/plus7/public?device=play&key={0}'
live_url = 'https://y7mobile.query.yahoo.com/v1/livestream/postcode/{0}'
oauth_consumer_key = 'dj0yJmk9QWJodDF5WDVnTGhwJmQ9WVdrOU1HODNiVXB0TnpnbWNHbzlNVGc0TWpnMk5UUTJNZy0tJnM9Y29uc3VtZXJzZWNyZXQmeD04Yw--'
oauth_consumer_secret = '0e4a80fc03b8ff1ed74a68a8dc583e77ff9e279b'

SSD_WV_REPO = 'https://github.com/glennguy/decryptmodules/raw/master/'
WIDEVINECDM_URL = { 'Linuxx86_64': 'https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb',
                    'Linuxarmv7': 'http://odroidxu.leeharris.me.uk/xu3/chromium-widevine-1.4.8.823-2-armv7h.pkg.tar.xz',
                    'Linuxarmv8': 'http://odroidxu.leeharris.me.uk/xu3/chromium-widevine-1.4.8.823-2-armv7h.pkg.tar.xz'}

UNARCHIVE_COMMAND = { 'Linuxx86_64': "(cd {1} && ar x {0} data.tar.xz && tar xJfO data.tar.xz ./opt/google/chrome/libwidevinecdm.so >{1}/{2} && chmod 755 {1}/{2} && rm -f data.tar.xz {0})",
                      'Linuxarmv7': "(cd {1} && tar xJfO {0} usr/lib/chromium/libwidevinecdm.so >{1}/{2} && chmod 755 {1}/{2} && rm -f {0})",
                      'Linuxarmv8': "(cd {1} && tar xJfO {0} usr/lib/chromium/libwidevinecdm.so >{1}/{2} && chmod 755 {1}/{2} && rm -f {0})"}
SSD_WV_DICT = { 'Windows': 'ssd_wv.dll',
                'Linux': 'libssd_wv.so',
                'Darwin': 'libssd_wv.dylib'}
WIDEVINECDM_DICT = { 'Windows': 'widevinecdm.dll',
                     'Linux': 'libwidevinecdm.so',
                     'Darwin': 'libwidevinecdm.dylib'}
SUPPORTED_PLATFORMS = [ 'WindowsAMD64',
                        'Windowsx86',
                        'Darwinx86_64',
                        'Linuxx86_64',
                        'Linuxarmv7',
                        'Linuxarmv8']

XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?><request protocol="3.0" 
version="chrome-55.0.2883.87" prodversion="55.0.2883.87" requestid="{{{0}}}" 
lang="en-US" updaterchannel="" prodchannel="" os="{1}" arch="{2}" 
nacl_arch="x86-64" wow64="1"><hw physmemory="12"/><os platform="Windows" 
arch="x86_64" version="10.0.0"/><app appid="oimompecagnajdejgnnjijobebaeigek" 
version="0.0.0.0" installsource="ondemand"><updatecheck/><ping rd="-2" 
ping_freshness=""/></app></request>"""

CRX_UPDATE_URL = "https://clients2.google.com/service/update2?cup2key=6:{0}&cup2hreq={1}"
