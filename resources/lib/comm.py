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
import time
import xbmcaddon
import xbmcgui

from aussieaddonscommon import exceptions
from aussieaddonscommon import session
from aussieaddonscommon import utils

ADDON = xbmcaddon.Addon()


def fetch_url(url, headers=None):
    """Simple function that fetches a URL using requests."""
    with session.Session() as sess:
        if headers:
            sess.headers.update(headers)
        request = sess.get(url)
        try:
            request.raise_for_status()
        except Exception as e:
            # Just re-raise for now
            raise e
        data = request.text
    return data


def api_query(key=None):
    if key:
        query_url = config.query_url.format(key)
    else:
        query_url = config.shows_url
    # deal with intermittient api timeout errors
    retries = 3
    while retries > 0:
        data = json.loads(fetch_url(query_url))
        if 'plus7' in data:
            key_name = 'plus7'
        else:
            key_name = 'plus7shows'
        if data[key_name]['error']:
            retries -= 1
        else:
            return data
    return None


def get_categories():
    """Fetch list of all shows divided by genre"""
    categories_list = []
    json_data = api_query()
    genre_data = json_data['plus7shows']['result'][0]['genre']

    for genre in genre_data.keys():
        categories_list.append(genre)
    if ' ' in categories_list:
        categories_list.remove(' ')
    if 'TV Snax' in categories_list:
        categories_list.remove('TV Snax')
    return categories_list


def get_index():
    """Fetch the index of all shows available"""
    series_list = []
    json_data = api_query()

    series_data = json_data['plus7shows']['result'][0]['show_data']

    for series in series_data:

        title = series_data[series]['title']

        # Don't show any 'promo' shows. They don't get returned by Brightcove
        blacklist = ['Extras', 'healthyMEtv', 'PREVIEW', 'TV Buzz', 'TV Snax']
        if any(x in title for x in blacklist):
            utils.log("Skipping series %s (hide extras)" % title)
            continue

        s = classes.Series()
        s.id = series
        s.title = title
        s.description = series_data[series].get('info')
        s.thumbnail = series_data[series].get('thumbnail')
        s.genre = list(series_data[series].get('genre', '').split(','))
        series_list.append(s)

    return series_list


def get_series(series_id):
    """Fetch the episode list for a given series ID"""
    program_list = []
    json_data = api_query(series_id)

    if not json_data['plus7']['result']:
        return program_list

    program_data = json_data['plus7']['result'][0]['episodes']

    # For single programs, we'll need to force the output to be
    # list of dicts.
    if type(program_data) == dict:
        program_data = [program_data]

    for program in program_data:
        try:
            p = classes.Program()
            p.id = program.get('id')
            p.bcid = program.get('bcid')
            p.title = program.get('show')
            p.description = program.get('abstract')
            p.thumbnail = program.get('image')

            if 'duration' in program.keys():
                p.duration = int(float(program['duration']))

            # Sometimes they leave out the episode information, so use show
            show = program.get('show')
            episode = program.get('episode', show)

            if episode:
                # Subtitle can be any one of:
                #    Sun 18 Mar, series 3 episode 30
                #    Sun 18 March, series 3 episode 30
                #    Dragon Invasion, series 1 episode 9
                #    Beyond The Blacklist - Episode 12
                #    Now on Sundays
                #    Conan O'Brian, 2001

                # Replace any MS Word 'dash' instances
                episode = episode.replace(u'\u2013', u'-')

                # Sometimes they embed unicode
                episode = episode.encode('ascii', 'ignore')

                # Sometimes they separate with a dash
                episode = episode.replace(' - ', ' , ')

                sub_split = episode.split(',')
                for sub in sub_split:
                    # utils.log("Testing for episode title: %s" % sub)

                    # Strip the stupid spacing either side
                    sub = sub.lstrip(" ").rstrip(" ")

                    # Convert to python compatible short day
                    sub = sub.replace("Tues ", "Tue ")
                    sub = sub.replace("Thurs ", "Thu ")
                    sub = re.sub("March$", "Mar", sub)

                    # Not a date - check for episode/series
                    episode = re.search('[Ee]pisode\s?(?P<episode>\d+)', sub)
                    if episode:
                        try:
                            p.episode = int(episode.group('episode'))
                        except Exception:
                            pass  # Not a number. Move on.

                        # Only check for series if we've previously
                        # found episode
                        series = re.search(
                            '[Ss](eries|eason)\s?(?P<series>\w+)', sub)
                        if series:
                            try:
                                p.season = int(series.group('series'))
                            except Exception:
                                pass  # Not a number. Move on.
                    else:
                        try:
                            # Try parsing the date
                            date = "%s %s" % (sub, p.get_year())
                            timestamp = time.mktime(
                                time.strptime(date, '%a %d %b %Y'))
                            p.date = datetime.date.fromtimestamp(timestamp)
                        except Exception:
                            # Not a date or contains 'episode' - must be title
                            if sub != '':
                                # Sometimes the actual title has a comma in it.
                                # We'll just reconstruct the parts in that case
                                if p.episode_title:
                                    p.episode_title = "%s, %s" % (
                                        p.episode_title, sub)
                                else:
                                    p.episode_title = sub
        except Exception:
            utils.log('Failed to parse program: %s' % program)

        program_list.append(p)

    return program_list


def get_program(program_id, bcid, live=False):
    """Fetch the program information and stream URL for a given program ID"""
    utils.log("Fetching program information for: %s" % program_id)
    key = config.BRIGHTCOVE_ACCOUNT[bcid]
    try:
        brightcove_url = config.BRIGHTCOVE_URL.format(bcid, program_id)
        data = fetch_url(brightcove_url, {'BCOV-POLICY': key})
    except Exception as e:
        raise exceptions.AussieAddonsException(
            "Error fetching program: %s " % str(e))

    if data == 'null':
        utils.log("Brightcove returned: '%s'" % data)
        raise exceptions.AussieAddonsException(
            "Error fetching program.")

    try:
        program_data = json.loads(data)
    except Exception:
        utils.log("Bad program data: %s" % program_data)
        raise Exception("Error decoding program information.")

    program = classes.Program()

    program.id = program_data.get('id')
    program.title = program_data.get('name')
    program.description = program_data.get('description')
    program.thumbnail = program_data.get('thumbnail')
    if 'text_tracks' in program_data:
        if len(program_data['text_tracks']) == 0:
            utils.log("No subtitles available for this program")
        else:
            utils.log("Subtitles are available for this program")
            program.subtitle = program_data['text_tracks'][0].get('src')

    # Try for MP4 file first
    mp4_list = []
    for source in program_data['sources']:
        if live:
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
            utils.log("Using {0}p MP4 stream".format(stream['RES']))
            return program

    # If no MP4 streams available, use DASH/Widevine
    for source in program_data['sources']:
        if source.get('container') is None:
            if 'key_systems' in source:
                if 'com.widevine.alpha' in source['key_systems']:
                    program.url = source.get('src')
                    program.drm_key = (source['key_systems']
                                             ['com.widevine.alpha']
                                             ['license_url'])
                    utils.log("Using MPEG DASH stream...")
    return program


def get_live():
    """Fetch live channel info for available channels"""
    post_code = ADDON.getSetting('post_code')
    url = config.live_url.format(post_code)
    data = fetch_url(url)
    json_data = json.loads(data)
    if json_data['channels']['result'][0]['valid_postcode'] is False:
        utils.log('Invalid Post Code')
        xbmcgui.Dialog().ok('Invalid Post Code',
                            'Please enter a valid post code and try again')
        ADDON.openSettings()
        return

    channel_list = []

    for channel in json_data['channels']['result'][0]['asset']:
        c = classes.Program()
        c.thumbnail = channel['thumbnails']['large'].get('url')
        c.title = channel.get('title')
        c.description = channel['tvapiData']['schedule'][0].get('title')
        c.id = channel.get('thread_id')
        c.bcid = channel.get('brightcove_account_id')
        channel_list.append(c)

    return channel_list
