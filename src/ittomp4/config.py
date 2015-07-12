# -*- coding: utf-8-unix -*-

from __future__ import division, absolute_import

from collections import namedtuple

VideoConfig = namedtuple('VideoConfig', ('width', 'height', 'fps'))
AudioConfig = namedtuple('AudioConfig', ('fps'))

Config = namedtuple('Config', ('video', 'audio'))
