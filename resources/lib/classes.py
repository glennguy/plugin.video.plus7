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

import datetime
import re
import time
import urllib

import utils


class Series(object):

    def __init__(self):
        self.id = None
        self.thumbnail = None
        self.title = None
        self.description = None

    def __repr__(self):
        return self.title

    def __cmp__(self, other):
        return cmp(self.get_sort_title(), other.get_sort_title())

    def get_sort_title(self):
        """ Return a munged version of the title which
            forces correct sorting behaviour.
        """
        sort_title = self.title.lower()
        sort_title = sort_title.replace('the ', '')
        return sort_title

    def get_title(self):
        """ Return the program title, including the Series X part
            on the end.
        """
        return utils.descape(self.title)

    def get_list_title(self):
        """ Return the program title with the number of episodes
            together for the XBMC list
        """
        return "%s (%d)" % (self.get_title(), self.get_num_episodes())

    def get_title(self):
        """ Return the program title, including the Series X part
            on the end.
        """
        return utils.descape(self.title)

    def get_thumbnail(self):
        return self.thumbnail

    def get_description(self):
        return self.description


class Program(object):

    def __init__(self):
        self.id = None
        self.title = ''
        self.description = ''
        self.episode_title = None
        self.episode = None
        self.season = None
        self.category = None
        self.rating = None
        self.duration = 0
        self.date = None
        self.thumbnail = ''
        self.url = None

    def __repr__(self):
        return self.title

    def __cmp__(self, other):
        return cmp(self.title, other.title)

    def get_title(self):
        """ Return the program title, including the Series X part
            on the end.
        """
        return utils.descape(self.title)

    def get_episode_title(self):
        """ Return a string of the shorttitle entry, unless its    not 
            available, then we'll just use the program title instead.
        """
        if self.episode_title:
            return utils.descape(self.episode_title)

    def get_list_title(self):
        """ Return a string of the title, nicely formatted for XBMC list
        """
        title = self.get_title() 
    
        if (self.get_season() and self.get_episode()):
            # Series and episode information
            title = "%s (S%02dE%02d)" % (title, self.get_season(), self.get_episode())
        else:
            if self.get_episode():
                # Only episode information
                title = "%s (E%02d)" % (title, self.get_episode())
            else:
                if not self.get_episode_title():
                    if self.date:
                        # Date only, no episode information or episode title
                        title = "%s (%s)" % (title, self.get_date())

        if self.get_episode_title():
            title = "%s: %s" % (title, self.get_episode_title())

        return title

    def get_description(self):
        """ Return a string the program description, after running it through
            the descape.
        """
        return utils.descape(self.description)

    def get_category(self):
        """ Return a string of the category. E.g. Comedy
        """
        if self.category:
            return utils.descape(self.category)

    def get_rating(self):
        """ Return a string of the rating. E.g. PG, MA
        """
        if self.rating:
            return utils.descape(self.rating)

    def get_duration(self):
        """ Return the duration of the program in minutes
        """
        if self.duration > 0:
            # Really short shows round up to 1 min
            if self.duration < 60:
                return 1
            else:
                return self.duration/60

    def get_duration_string(self):
        """ Return a string representing the duration of the program.
            E.g. 00:30 (30 minutes) from a given string of seconds
        """
        if self.duration > 0:
            sec = self.duration
            hrs = sec / 3600
            sec -= 3600*hrs
            mins = sec / 60
            sec -= 60*mins
            return "%s:%s" % (hrs, mins)

    def get_date(self):
        """ Return a string of the date in the format 2010-02-28
            which is useful for XBMC labels.
        """
        if self.date:
            return self.date.strftime("%Y-%m-%d")

    def get_year(self):
        """ Return an integer of the year of publish date
        """
        if self.date:
            return self.date.year
        else:
            return datetime.datetime.now().year

    def get_season(self):
        """ Return an integer of the Series, discovered by a regular
            expression from the orginal title, unless its not available,
            then the year will be returned.
        """
        if self.season:
            return self.season

    def get_episode(self):
        """ Return an integer of the Episode, discovered by a regular
            expression from the orginal title, unless its not available,
            then a 0 will be returned.
        """
        if self.episode:
            return self.episode

    def get_thumbnail(self):
        """ Returns the thumbnail
        """
        return utils.descape(self.thumbnail)
            
    def get_url(self):
        """ Returns the URL for the video stream
        """
        return self.url

    def get_xbmc_list_item(self):
        """ Returns a dict of program information, in the format which
            XBMC requires for video metadata.
        """
        d = {}
        if self.get_title():         d['tvshowtitle'] = self.get_title()
        if self.get_episode_title(): d['title'] = self.get_episode_title()
        if self.get_category():      d['genre'] = self.get_category()
        if self.get_description():   d['plot'] = self.get_description()
        if self.get_description():   d['plotoutline'] = self.get_description()
        if self.get_duration():      d['duration'] = self.get_duration()
        if self.get_year():          d['year'] = self.get_year()
        if self.get_date():          d['aired'] = self.get_date()
        if self.get_season():        d['season'] = self.get_season()
        if self.get_episode():       d['episode'] = self.get_episode()
        if self.get_rating():        d['mpaa'] = self.get_rating()
        if self.get_url():           d['url'] = self.get_url()
        return d

    def get_xbmc_audio_stream_info(self):
        """
            Return an audio stream info dict
        """
        d = {}
        # This information may be incorrect
        d['codec']    = 'aac'
        d['language'] = 'en'
        d['channels'] = 2
        return d

    def get_xbmc_video_stream_info(self):
        """
            Return a video stream info dict
        """
        d = {}
        d['codec']  = 'h264'
        if self.get_duration(): 
            d['duration'] = self.get_duration()
        return d
