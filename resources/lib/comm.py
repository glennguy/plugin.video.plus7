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
import datetime
import json
import re
import threading
import time
import urllib
import urllib2

import xbmc
import xbmcaddon

import m3u8
import oauth2 as oauth

from hashlib import md5

import config
import utils
import classes

addon = xbmcaddon.Addon(config.ADDON_ID)

def fetch_url(url):
    """
        Simple function that fetches a URL using urllib2.
        An exception is raised if an error (e.g. 404) occurs.
    """
    utils.log("Fetching URL: %s" % url)
    http = urllib2.urlopen(urllib2.Request(url, None))
    return http.read()

def api_query(query):

    params = {
        'oauth_version': '1.0',
        'oauth_nonce': oauth.generate_nonce(),
        'oauth_timestamp': int(time.time()),
        'format': 'json',
        'q': query
    }

    consumer = oauth.Consumer(key=config.oauth_consumer_key, secret=config.oauth_consumer_secret)
    params['oauth_consumer_key'] = consumer.key
    req = oauth.Request(method="GET", url=config.api_url, parameters=params)
    signature_method = oauth.SignatureMethod_HMAC_SHA1()
    req.sign_request(signature_method, consumer, None)
    rs = urllib2.urlopen(req.to_url())
    return rs.read()

def get_index():
    """
        Fetch the index of all shows available
    """
    series_list = []
    data = api_query("select * from plus7.showlist where device = 'ios'")
    json_data = json.loads(data)

    series_data = json_data['query']['results']['json']['show_data']

    for series in series_data:

        title = series_data[series]['title']

        # Don't show any 'promo' shows. They don't get returned by Brightcove
        if (title.find('Extras') > -1 or 
                title.find('healthyMEtv') > -1):
            utils.log("Skipping series %s (hide extras)" % title)
            continue

        s = classes.Series()
        s.id = series
        s.title = series_data[series]['title']
        s.description = series_data[series]['info']
        if 'thumbnail' in series_data[series]:
            s.thumbnail = series_data[series]['thumbnail']
        series_list.append(s)

    return series_list

def get_series(series_id):
    """
        Fetch the episode list for a given series ID
    """
    program_list = []
    data = api_query("select * from plus7 where key = '%s' and device = 'ios'" % series_id)
    json_data = json.loads(data)

    program_data = json_data['query']['results']['json']['episodes']

    # For single programs, we'll need to force the output to be
    # list of dicts.
    if type(program_data) == dict:
        program_data = [program_data]

    for program in program_data:
        p = classes.Program()
        p.id = program['id']
        p.title = program['show']
        p.description = program['abstract']
        p.thumbnail = program['image']

        if 'duration' in program.keys():
            p.duration = int(float(program['duration']))

        # Sometimes they leave out the episode information
        if program.has_key('episode') and program['episode'] is not None:
            episode = program['episode']
        else:
            episode = program['show']

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
            #utils.log("Testing for episode title: %s" % sub)

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
                    #utils.log("%s - Episode found: '%s'" % (sub, p.episode))
                except:
                    pass # Not a number. Move on.

                # Only check for series if we've previously found episode
                series = re.search('[Ss](eries|eason)\s?(?P<series>\w+)', sub)
                if series:
                    try:
                        p.season = int(series.group('series'))
                        #utils.log("%s - Season found: '%s'" % (sub, p.season))
                    except:
                        pass # Not a number. Move on.
            else:
                try:
                    # Try parsing the date
                    date = "%s %s" % (sub, p.get_year())
                    timestamp = time.mktime(time.strptime(date, '%a %d %b %Y'))
                    p.date = datetime.date.fromtimestamp(timestamp)
                    #utils.log("%s - Date found: '%s'" % (sub, p.date))
                except:
                    # Not a date or contains 'episode' - must be title
                    if sub != '':
                        # Sometimes the actual title has a comma in it. We'll just reconstruct
                        # the parts in that case
                        if p.episode_title:
                            p.episode_title = "%s, %s" % (p.episode_title, sub)
                        else:
                            p.episode_title = sub
                        #utils.log("%s - Episode title found: '%s'" % (sub, p.episode_title))


        program_list.append(p)

    return program_list


def get_program(program_id):
    """
        Fetch the program information and streaming URL for a given
        program ID
    """
    try:
        brightcove_url = "https://api.brightcove.com/services/library?command=find_video_by_reference_id&reference_id=%s&media_delivery=HTTP_IOS&video_fields=id,name,shortDescription,videoStillURL,length,FLVURL,captioning&token=BMG-nlpt1dDQcdqz-EIBAUNRGtXnLQv-gbltLyHgproxck0YUZfnkA.." % program_id
        data = fetch_url(brightcove_url)
    except:
        raise Exception("Error fetching program information, possibly unavailable.")

    if data == 'null':
        utils.log("Brightcove returned: '%s'" % data)
        raise Exception("Error fetching program information, possibly unavailable.")

    try:
        program_data = json.loads(data)
    except:
        utils.log("Bad program data: %s" % program_data)
        raise Exception("Error decoding program information.")

    program = classes.Program()

    program.id = program_data['id']
    program.title = program_data['name']
    program.description = program_data['shortDescription']
    program.thumbnail = program_data['videoStillURL']
    if program_data.has_key('captioning'):
        if program_data['captioning'] == None:
            utils.log("No subtitles available for this program")
        else:
            utils.log("Subtitles are available for this program")
            program.subtitle = program_data['captioning']['captionSources'][0]['url']

    if addon and addon.getSetting('video_transport') == 'Native mode (XBMC v13, Kodi v14+)':
        # Use Apple iOS HLS stream directly
        # This requires gnutls support in ffmpeg, which is only found in XBMC v13
        # but not available at all in iOS or Android builds
        utils.log("Using native HTTPS HLS stream handling...")
        program.url = program_data['FLVURL']
    else:
        # Use Adam M-W's implementation of handling the HTTPS business within
        # the m3u8 file directly. He's a legend.
        utils.log("Using stream compatibility mode...")
        program.url = get_m3u8(program_data['id'])

    return program

def get_m3u8(video_id):
    brightcove_url = 'http://c.brightcove.com/services/mobile/streaming/index/master.m3u8?videoId=%s' % video_id
    index_m3u8 = m3u8.load(brightcove_url)

    # Get the highest bitrate video
    rendition_uri = sorted(index_m3u8.playlists, key=lambda playlist: playlist.stream_info.bandwidth)[0].uri

    # Download the rendition and modify the key uris
    (rendition_m3u8_path, keys) = download_rendition(rendition_uri, video_id)

    # Download the keys
    download_keys(keys)

    return rendition_m3u8_path


def get_temp_dir(video_id):
    topdir = os.path.join(xbmc.translatePath('special://temp/'), config.ADDON_ID)
    if not os.path.isdir(topdir):
        os.mkdir(topdir)

    dirname = 'brightcove_%s' % video_id
    path = os.path.join(topdir, dirname)
    if not os.path.isdir(path):
        os.mkdir(path)
    return path


def download_rendition(rendition_uri, video_id):
    temp_dir = get_temp_dir(video_id)
    utils.log('Downloading rendition file from "%s" to "%s"...' % (rendition_uri, temp_dir))
    rendition_m3u8_path = os.path.join(temp_dir, 'rendition.m3u8')
    rendition_m3u8_file = open(rendition_m3u8_path, 'w')
    rendition_m3u8_response = urllib.urlopen(rendition_uri)
    keys = []
    for line in rendition_m3u8_response:
        match = re.match('#EXT-X-KEY:METHOD=AES-128,URI="(https://.+?)"', line)
        if match:
            key_url = match.group(1)
            key_path = os.path.join(temp_dir, "keyfile_%s.key" % md5(key_url).hexdigest())
            keys.append((key_path, key_url))
            rendition_m3u8_file.write('#EXT-X-KEY:METHOD=AES-128,URI="%s"\n' % key_path)
        else:
            rendition_m3u8_file.write(line)
    rendition_m3u8_file.close()
    return (rendition_m3u8_path, keys)

def download_key(key_path, key_url):
    urllib.urlretrieve(key_url, key_path)

def download_keys(keys):
    utils.log('Downloading HLS key files...')

    threads = []
    for key in keys:
        thread = threading.Thread(target=download_key, args=key)
        thread.daemon = True
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
