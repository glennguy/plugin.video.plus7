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

	stream = comm.get_stream(params['id'])

	if not stream:
		d = xbmcgui.Dialog()
		msg = utils.dialog_message("Error: Stream not availble.\nPlus7 will only work within Australia.")
		d.ok(*msg)
		utils.log_error();
		return

	try:
		# Build the final RTMP Url. New syntax for external librtmp
		# http://trac.xbmc.org/ticket/8971
		rtmp_url = "%s playpath=%s swfurl=%s swfvfy=true" % (stream['rtmp_host'], stream['rtmp_path'], config.swf_url)
	
		listitem=xbmcgui.ListItem(label=p.title, iconImage=p.thumbnail, thumbnailImage=p.thumbnail)
		listitem.setInfo('video', p.get_xbmc_list_item())
	
		xbmc.Player().play(rtmp_url, listitem)
	except:
		# oops print error message
		d = xbmcgui.Dialog()
		message = utils.dialog_error("Unable to play video")
		d.ok(*message)
		utils.log_error();
