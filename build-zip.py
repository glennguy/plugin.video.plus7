#!/usr/bin/env python

import os
import zipfile
from xml.dom.minidom import parse


ADDON='plugin.video.catchuptv.au.plus7'

# Parse addon.xml for version number
dom = parse("%s/addon.xml" % ADDON)
addon = dom.getElementsByTagName('addon')[0]
version = addon.getAttribute('version')
zfilename = "%s-%s.zip" % (ADDON, version)

# Walk the directory to create the zip file
z = zipfile.ZipFile(zfilename, 'w')
for root, subFolders, files in os.walk(ADDON):
  for f in files:
    if f.endswith('.swp') or 
    z.write(os.path.join(root, f), os.path.join(root, f))
z.close()

