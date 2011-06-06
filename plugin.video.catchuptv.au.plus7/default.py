import sys

import resources.lib.utils as utils
import resources.lib.series as series
import resources.lib.programs as programs
import resources.lib.play as play

# plugin constants
__plugin__  = "Plus7"
__author__  = "Andy Botting"
__url__     = "http://xbmc-boxee-iview.googlecode.com"
__svn_url__ = "https://xbmc-boxee-iview.googlecode.com/svn/trunk/xbmc/abc_iview"
__version__ = "0.0.3"

print "[PLUGIN] '%s: version %s' initialized!" % (__plugin__, __version__)

if __name__ == "__main__" :
	params_str = sys.argv[2]
	params = utils.get_url(params_str)

	if (len(params) == 0):
		series.make_series_list()
	else:
		if params.has_key("series_id"):
			programs.make_programs_list(params_str)
		elif params.has_key("play"):
			play.play(params_str)
