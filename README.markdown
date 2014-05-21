Plus7 plugin for XBMC
================================

This plugin provides a simple list of available programs from the Plus7
web site, and allows you to stream them with XBMC.

The content is only available with Australia, or you can apparently use sites
like Unblock-US, UnoTelly or Tunlr.net (free). or your own VPN solution which
terminates in with an AU IP address.

This addon relies on the mobile stream for iOS and Android. This used the HLS
stream, which requires HTTPS support. We support native support for new
platforms (XBMC v13 Gotham, excluding Android and iOS), but provide a fallback for
other platforms (e.g. XBMC v12 Frodo and Android/iOS).

Thanks for contributions from:
  * Adam M-W


Installation
------------
The latest stable release of this add-on is available as part of the
[XBMC CatchUp TV AU repository] [repository].

For the latest development version, you can grab the [GitHub generated ZIP file] [githubzip].

Simply download the ZIP file to your XBMC device and install through the menu via
System -> Settings -> Add-ons -> Install from zip file

Issues
------
If you find an issue, please test with the latest version of XBMC. I would
recommend XBMC v13.1 Gotham or later.

If you're using a Raspberry Pi or another dedicated HTPC, I would recommend
using [OpenELEC] [openelec].

For any other issues or bug reports, please file them on the [issues page] [issues].

Please include log output if possible, using Github Gist or Pastebin.com.

The location of your XBMC log file will depend on your platform.

For Windows:
```
%APPDATA%\XBMC\temp\xbmc.log
```

For Linux:
```
~/.xbmc/temp/xbmc.log
```

For Mac OS X:
```
~/Library/Application Support/XBMC/temp/xbmc.log
```

For AppleTV:
```
/Users/frontrow/Library/Application Support/XBMC/temp/xbmc.log
```

Contact Me
----------
For anything else, you can contact me by email at andy#andybotting.com

[repository]: http://code.google.com/p/xbmc-catchuptv-au
[githubzip]: https://github.com/andybotting/xbmc-addon-plus7/archive/master.zip
[openelec]: http://openelec.tv/
[issues]: https://github.com/andybotting/xbmc-addon-plus7/issues
