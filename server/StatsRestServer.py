#!/usr/bin/env python

#------------------------------------------------------------------------------
# Date: 1/7/2013
# Author:   delapsley@gmail.com
# Description:
#
#   Simple stats server implemented for a VDAS demonstration. This server
#   reads data from a data acquisition system via an XML interface and then
#   publishes it via a RESTful interface.
#
#   The StatServer class is responsible for acquiring the data, and then 
#   serving it up. It can either acquire data from a live system, or generate
#   fake data.
#
#   To generate and publish a fake data stream, use a command line similar to:
#
#       $ python StatsServer.py -F
#
#   The FakeData class handles fake data generation.
#
#   The parse_stats() function is responsible for handling the XML response
#   from the data acquisition system.
#------------------------------------------------------------------------------

import getopt
import random
import re
import socket
import string
import sys
import time
import web
from copy import copy
from threading import Thread
from xml.etree.ElementTree import fromstring
from SimpleXMLRPCServer import SimpleXMLRPCServer

urls = (
    '/', 'Index',
    '/interface/(\d+)', 'Interface',
    '/ethernet/(\d+)', 'Ethernet',
    '/capture', 'Capture',
)

class Index:

    def GET(self):
        print 'hello'


class Interface:

    def GET(self, id):
        return 'hello, %s' % id

class Ethernet:

    def GET(self, id):
        print 'ethernet, ', id


class Capture:

    def GET(self, id):
        print 'capture, ', id


app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()
