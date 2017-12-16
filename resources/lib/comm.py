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
import classes
import config
import datetime
import json
import m3u8
import re
import sys
import time
import urllib
import urlparse
import uuid
import xbmcaddon
import xbmcgui

from aussieaddonscommon import exceptions
from aussieaddonscommon import session
from aussieaddonscommon import utils

ADDON = xbmcaddon.Addon()


def fetch_url(url, headers=None, retries=1):
    """Simple function that fetches a URL using requests."""
    with session.Session() as sess:
        if headers:
            sess.headers.update(headers)
        while retries > 0:
            try:
                request = sess.get(url)
                data = request.text
                return data
            except session.requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    retries -= 1
                else:
                    raise e
                if retries == 0:
                    raise e
    return data


def get_market_id():
    try:
        data = json.loads(fetch_url(config.MARKET_URL, retries=3))  #sometimes 404s
        return str(data.get('_id'))
    except session.requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return '15'
    
def api_query(key=None):
    market_id = get_market_id()
    headers = {'market-id': market_id, 'api-version': config.API_VER}
    if not key:
        key = 'home'
    query_url = urlparse.urljoin(config.CONTENT_URL, key)
    # deal with intermittient api timeout errors
    data = json.loads(fetch_url(query_url, headers=headers))
    return data


def get_categories():
    """Fetch list of all genres"""
    categories_list = []
    json_data = api_query()
    for item in json_data.get('items'):
        if item.get('title') == 'Categories':
            genre_data = item
            break

    for genre in genre_data.get('linkImageItems'):
        c = classes.Category()
        c.title = genre.get('title')
        c.thumb = genre['image'].get('url')
        c.url = urlparse.urljoin(config.CONTENT_URL, genre['contentLink'].get('url').lstrip('/'))
        categories_list.append(c)
    return categories_list


def get_series_list(params):
    """Fetch the index of all shows available for a given category"""
    series_list = []
    json_data = api_query(params.get('url'))

    for item in json_data.get('items'):
        if 'mediaItems' not in item:
            continue
        for series in item.get('mediaItems'):
            s = classes.Series()
            s.title = series['image'].get('name').lstrip()
            s.thumb = series['image'].get('url')
            s.url = urlparse.urljoin(config.CONTENT_URL, series['contentLink'].get('url').lstrip('/'))
            series_list.append(s)

    return series_list


def get_programs_list(params):
    """Fetch the episode list for a given series"""
    series_url = params.get('url')
    program_list = []
    json_data = api_query(series_url)

    for item in json_data.get('items'):
        if item.get('title') == 'Shelf Container':
            for sub_item in item['items']:
                if not sub_item.get('items'):
                    continue
                for sub_item_2 in sub_item['items']:
                    for episode in sub_item_2.get('items'):
                        p = classes.Program()
                        p.title = episode['cardData']['image'].get('name')
                        p.thumb = episode['cardData']['image'].get('url')
                        p.description = episode['cardData'].get('synopsis')
                        p.url = episode['playerData'].get('videoUrl')
                        try:
                            # Try parsing the date
                            date = episode['infoPanelData'].get('airDate')
                            timestamp = time.mktime(
                                time.strptime(date, '%d &b %Y'))
                            p.date = datetime.date.fromtimestamp(timestamp)
                        except:
                            pass
                        utils.log('added program')
                        program_list.append(p)

    return program_list


def get_program(params):
    """Fetch the program information and stream URL for a given program ID"""
    utils.log('Fetching program information for: {0}'.format(
        params.get('title')))

    program = classes.Program()
    program.parse_xbmc_url(sys.argv[2])
    program_url = program.format_url(params.get('url'))
    data = fetch_url(program_url)

    try:
        program_data = json.loads(data)
    except Exception:
        utils.log("Bad program data: %s" % program_data)
        raise Exception("Error decoding program information.")

    if 'text_tracks' in program_data.get('media'):
        if len(program_data['media'].get('text_tracks')) == 0:
            utils.log("No subtitles available for this program")
        else:
            utils.log("Subtitles are available for this program")
            program.subtitle = program_data['media']['text_tracks'][0].get('src')
    
    # If no DASH streams available, use MP4
    mp4_list = []
    for source in program_data['media'].get('sources'):
        if program.live:
            index_m3u8 = m3u8.load(source.get('src'))
            # Get the highest bitrate video
            program.url = (sorted(
                index_m3u8.playlists,
                key=lambda playlist: int(playlist.stream_info.bandwidth))
                    [-1].uri)
            return program
        if source.get('container') == 'MP4':
            src = source.get('src')
            if src:
                res = source.get('height')
                mp4_list.append({'SRC': src, 'RES': res})
    if len(mp4_list) > 0:
        sorted_mp4_list = sorted(mp4_list,
                                 key=lambda x: x['RES'],
                                 reverse=True)
        stream = sorted_mp4_list[0]
        program.url = stream['SRC']
        utils.log(stream)
        if program.url:
            utils.log('Using {0}p MP4 stream'.format(stream['RES']))
            return program
    # Try for DASH first if enabled
    for source in program_data['media'].get('sources'):
        if source.get('type') == 'application/dash+xml':
            if 'hbbtv' in source.get('src'):
                continue
            program.url = source.get('src')
            program.dash = True
            utils.log('Using DASH stream...')
            if 'key_systems' in source:
                if 'com.widevine.alpha' in source['key_systems']:
                    program.drm_key = (source['key_systems']
                                             ['com.widevine.alpha']
                                             ['license_url'])
                    utils.log('Using DASH/Widevine stream...')
    return program

    


def get_live():
    """Fetch live channel info for available channels"""
    json_data = api_query()
    channel_list = []
    for item in json_data.get('items'):
        if item.get('title') == 'On Now':
            for channel in item.get('mediaItems'):
                c = classes.Program()
                c.live = True
                c.thumb = channel['channelLogo'].get('url')
                c.title = channel.get('name')
                c.description = channel['schedule'][0]['playerData'].get('synopsis')
                c.url = channel['schedule'][0]['playerData'].get('videoUrl')
                channel_list.append(c)

    return channel_list
