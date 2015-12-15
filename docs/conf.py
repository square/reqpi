import os
import sys

up = os.path.dirname(os.path.dirname(__file__))
sys.path.append(up)

from reqpi import _version

master_doc = 'index'
project = 'reqpi'
copyright = '2015, Square, Inc.'
author = 'Square, Inc.'
release = version = _version.get_versions()["version"]
