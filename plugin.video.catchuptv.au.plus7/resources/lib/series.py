"""
	Category module: fetches a list of categories to use as folders
"""

# main imports
import sys, os, re, urllib2, urllib
import comm

try:
	import xbmc, xbmcgui, xbmcplugin
except ImportError:
	pass # for PC debugging

BASE_SKIN_THUMBNAIL_PATH = os.path.join(os.getcwd(), 'resources', 'media')
BASE_PLUGIN_THUMBNAIL_PATH = os.path.join(os.getcwd(), 'resources', 'media')

def make_series_list():
	try:
		series_list = comm.get_index()
		series_list.sort()

		# fill media list
		ok = fill_series_list(series_list)
	except:
		# oops print error message
		print "ERROR: %s (%d) - %s" % (sys.exc_info()[2].tb_frame.f_code.co_name, sys.exc_info()[2].tb_lineno, sys.exc_info()[1])
		ok = False

	# send notification we're finished, successfully or unsuccessfully
	xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)


def fill_series_list(series_list):
	try:
		ok = True
		# enumerate through the list of categories and add the item to the media list
		for s in series_list:
			url = "%s?series_id=%s" % (sys.argv[0], s.get_series_url())
			icon = "defaultfolder.png"
			listitem = xbmcgui.ListItem(s.get_title(), iconImage=icon)

			# add the item to the media list
			ok = xbmcplugin.addDirectoryItem(
						handle=int(sys.argv[1]), 
						url=url, 
						listitem=listitem, 
						isFolder=True, 
						totalItems=len(series_list)
					)
			# if user cancels, call raise to exit loop
			if (not ok): 
				raise
	except:
		# user cancelled dialog or an error occurred
		d = xbmcgui.Dialog()
		d.ok('Plus7 Error', 'Plus7 encountered an error:', '  %s (%d) - %s' % (sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ]) )
		return None

		# user cancelled dialog or an error occurred
		print "ERROR: %s (%d) - %s" % (sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ],)
		ok = False
	return ok

