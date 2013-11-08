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
