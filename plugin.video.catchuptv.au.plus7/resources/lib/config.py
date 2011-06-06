import os

version     = '0.0.1'

# os.uname() is not available on Windows, so we make this optional.
try:
	uname = os.uname()
	os_string = ' (%s %s %s)' % (uname[0], uname[2], uname[4])
except AttributeError:
	os_string = ''

user_agent = 'Plus7 plugin for XBMC %s%s' % (version, os_string)

index_url = "http://au.tv.yahoo.com/plus7/browse/"

series_url = "http://au.tv.yahoo.com/plus7/%s/"
program_url = "http://au.tv.yahoo.com%s"
program_info_url = "http://cosmos.bcst.yahoo.com/rest/v2/pops;id=%s;lmsoverride=1"
stream_info_url = "http://cosmos.bcst.yahoo.com/rest/v2/pops;id=%s;lmsoverride=1;element=stream;bw=1200"

# Used for "SWF verification", a stream obfuscation technique
swf_url     = "http://d.yimg.com/m/up/ypp/au/player.swf"
