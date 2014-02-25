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

import urllib, urllib2
import config
import classes
import utils
import re
import datetime
import time
import random
import math

import json
import oauth2 as oauth


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
        s = classes.Series()
        s.id = series
        s.title = series_data[series]['title']
        s.description = series_data[series]['info']
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
            utils.log("Testing for episode title: %s" % sub)

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
                    utils.log("%s - Episode found: '%s'" % (sub, p.episode))
                except:
                    pass # Not a number. Move on.

                # Only check for series if we've previously found episode
                series = re.search('[Ss](eries|eason)\s?(?P<series>\w+)', sub)
                if series:
                    try:
                        p.season = int(series.group('series'))
                        utils.log("%s - Season found: '%s'" % (sub, p.season))
                    except:
                        pass # Not a number. Move on.
            else:
                try:
                    # Try parsing the date
                    date = "%s %s" % (sub, p.get_year())
                    timestamp = time.mktime(time.strptime(date, '%a %d %b %Y'))
                    p.date = datetime.date.fromtimestamp(timestamp)
                    utils.log("%s - Date found: '%s'" % (sub, p.date))
                except:
                    # Not a date or contains 'episode' - must be title
                    if sub != '':
                        # Sometimes the actual title has a comma in it. We'll just reconstruct
                        # the parts in that case
                        if p.episode_title:
                            p.episode_title = "%s, %s" % (p.episode_title, sub)
                        else:
                            p.episode_title = sub
                        utils.log("%s - Episode title found: '%s'" % (sub, p.episode_title))


        program_list.append(p)

    return program_list


def get_program(program_id):
    """
        Fetch the program information and streaming URL for a given
        program ID
    """
    brightcove_url = "https://api.brightcove.com/services/library?command=find_video_by_reference_id&reference_id=%s&media_delivery=HTTP_IOS&video_fields=id,name,shortDescription,videoStillURL,length,FLVURL&token=BMG-nlpt1dDQcdqz-EIBAUNRGtXnLQv-gbltLyHgproxck0YUZfnkA.." % program_id
    data = fetch_url(brightcove_url)
    program_data = json.loads(data)

    program = classes.Program()

    program.id = program_data['id']
    program.title = program_data['name']
    program.description = program_data['shortDescription']
    program.thumbnail = program_data['videoStillURL']
    
    # Apple iOS HLS stream
    program.url = program_data['FLVURL']

    # High-quality WMV - doesn't play after about 10 seconds
    #program.url = program_data['WVMRenditions'][-1]['url']

    return program
