import sys
import config
import utils
import classes
import comm

try:
	import xbmc, xbmcgui, xbmcplugin, xbmcaddon
except ImportError:
	pass # for PC debugging

def play(url):
	params = utils.get_url(url)	
	
	p = classes.Program()
	p.parse_xbmc_url(url)

	try:

		stream = comm.get_stream(params['id'])

		# Build the final RTMP Url. New syntax for external librtmp
		# http://trac.xbmc.org/ticket/8971
		rtmp_url = "%s playpath=%s swfurl=%s swfvfy=true" % (stream['rtmp_host'], stream['rtmp_path'], config.swf_url)
	
		listitem=xbmcgui.ListItem(label=p.title, iconImage=p.thumbnail, thumbnailImage=p.thumbnail)
		listitem.setInfo('video', p.get_xbmc_list_item())
	
		xbmc.Player().play(rtmp_url, listitem)
	except:
		# user cancelled dialog or an error occurred
		d = xbmcgui.Dialog()
		d.ok('Plus7 Error', 'Plus7 encountered an error:', '  %s (%d) - %s' % (sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ]) )
		return None
		print "ERROR: %s (%d) - %s" % ( sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
