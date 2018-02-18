import classes
import config
import datetime
import json
import sys
import time
import urlparse
import xbmcaddon

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
        data = json.loads(fetch_url(config.MARKET_URL, retries=3))
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
        c.url = urlparse.urljoin(
            config.CONTENT_URL, genre['contentLink'].get('url').lstrip('/'))
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
            s.url = urlparse.urljoin(
                config.CONTENT_URL,
                series['contentLink'].get('url').lstrip('/'))
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
    dash_preferred = ADDON.getSetting('dash_enabled') == 'true'

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
            program.subtitle = (program_data['media']['text_tracks'][0]
                                .get('src'))

    for source in program_data['media'].get('sources'):
        # Get DASH URL
        if source.get('type') == 'application/dash+xml':
            if 'hbbtv' in source.get('src'):
                continue
            program.dash_url = source.get('src')
            program.dash_preferred = dash_preferred
            utils.log('Found DASH stream: {0}'.format(program.dash_url))
            if 'key_systems' in source:
                if 'com.widevine.alpha' in source['key_systems']:
                    program.drm_key = (source['key_systems']
                                             ['com.widevine.alpha']
                                             ['license_url'])
                    utils.log('DASH stream using Widevine')
        # Get HLS URL
        elif source.get('type') in ['application/x-mpegURL',
                                    'application/vnd.apple.mpegurl']:
            if 'key_systems' in source:
                continue
            if source.get('ext_x_version') != '5':
                program.hls_url = source.get('src')
                utils.log('Found HLS stream: {0}'.format(program.hls_url))
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
                c.description = (channel['schedule'][0]['playerData']
                                 .get('synopsis'))
                c.url = channel['schedule'][0]['playerData'].get('videoUrl')
                channel_list.append(c)

    return channel_list
