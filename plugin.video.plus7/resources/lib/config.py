import os

NAME = 'Plus7'
VERSION = '1.1'

try:
	uname = os.uname()
	os_string = ' (%s %s %s)' % (uname[0], uname[2], uname[4])
except AttributeError:
	os_string = ''

user_agent = '%s v%s plugin for XBMC %s' % (NAME, VERSION, os_string)

index_url = "http://au.tv.yahoo.com/plus7/browse/"
series_url = "http://au.tv.yahoo.com/plus7/%s/"
program_metadata_url = "http://cosmos.bcst.yahoo.com/rest/v2/pops;id=%s;lmsoverride=1"
program_url = "http://au.tv.yahoo.com"
stream_url = "http://video.query.yahoo.com"
