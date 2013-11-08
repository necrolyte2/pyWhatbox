pyWhatbox
=========

Python goodies for Whatbox related stuff

Examples
========

Show all current downloads
```
from whatbox import WhatboxXMLRPC
w = WhatBoxXMLRPC(
    'quartz.whatbox.ca',
    'myuser',
    'mypass'
)

print w.get_all_files()
```

Misc Goodies
============

* viewdownloads.py is a script to easily just list all your downloads
* wb_sync_completed.py is a script to sync all completed downloads to a folder on your computer


TODO
====

* Change project so it is an actualy Python package
* Add remove/delete torrent methods to WhatboxXMLRPC class
* Modify wb_sync_completed.py so it uses urllib functionality or something similar so
  it is 100% python and doesn't rely on using aria2c
