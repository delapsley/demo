# Create your views here.

#------------------------------------------------------------------------------
# Date: 1/13/2013
# Author: delapsley@gmail.com
# Description:
#
#   This view implements a very simple RESTful API for serving up data to the
#   gviz widgets. Incoming requests are mapped to one of:
#
#       * interface
#       * ethernet
#       * capture
#
#   Which then call out to the XML RPC server via a ServerProxy to obtain data
#   from the Data Acquisition System.
#------------------------------------------------------------------------------

import gviz_api
import re
import random
import socket
import time

from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render_to_response
from xml.dom.minidom import Document
from xmlrpclib import ServerProxy
from xml.etree.ElementTree import fromstring

#------------------------------------------------------------------------------
# Globals
#------------------------------------------------------------------------------
SOCKET_TIMEOUT = 2
NUM_INTERFACES = 4

def get_proxy():
    # Connect to XML RPC server.
    proxy = None
    try:
        proxy = ServerProxy('http://localhost:9000/')
        socket.setdefaulttimeout(SOCKET_TIMEOUT)
    except Exception, e:
        print 'Connect timeout: %s'%e

    return proxy

#------------------------------------------------------------------------------
# Resources
#------------------------------------------------------------------------------
def interface(request):
    '''Resource for interface data.'''

    proxy = get_proxy()

    # Describe data.
    description = {
        'interface': ('string', 'Interface'),
        'byteCount': ('number', 'byteCount'),
        'bytesDropped': ('number', 'bytesDropped'),
        'packetCount': ('number', 'packetCount'),
        'packetsDropped': ('number', 'packetsDropped'),
        'errorCount': ('number', 'errorCount'),
        }

    # Retrieve data
    data = []
    labels = [ 'interface', 'byteCount', 'bytesDropped', 'packetCount',
               'packetsDropped', 'errorCount' ]
    try:
        for i in range(NUM_INTERFACES):
            data.append(dict(zip(labels,
                                 [int(x) for x in proxy.interface(str(i))])))
    except Exception, e:
        print 'Data timeout: %s'%e
        for i in range(NUM_INTERFACES):
            data.append(dict(zip(labels, [0 for x in range(len(labels))])))

    # Package data as data table.
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)

    # Convert to json and return.
    req_id = request.GET['tqx'].split(':')[1]
    json = data_table.ToJSonResponse(columns_order=labels, req_id=req_id)
    return HttpResponse(str(json), mimetype='text/plain')


def ethernet(request):
    '''Resource for ethernet data.'''

    proxy = get_proxy()

    description = {
        'label': ('string', 'Label'),
        'value': ('number', 'Value'),
        }

    data = None
    try:
        data = [
            {'label': 'Eth0', 'value': proxy.ethernet('0'), },
            {'label': 'Eth1', 'value': proxy.ethernet('1'), },
            {'label': 'Eth2', 'value': proxy.ethernet('2'), },
            {'label': 'Eth3', 'value': proxy.ethernet('3'), },
            ]
    except Exception, e:
        print 'ETHERNET: %s'%e
        data = [
            {'label': 'Eth0', 'value': 0, },
            {'label': 'Eth1', 'value': 0, },
            {'label': 'Eth2', 'value': 0, },
            {'label': 'Eth3', 'value': 0, },
            ]

    # Package data in data table.
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)

    # Convert to json and return.
    req_id = request.GET['tqx'].split(':')[1]
    json = data_table.ToJSonResponse(columns_order=('label', 'value'),
                                     order_by="label", req_id=req_id)
    return HttpResponse(str(json), mimetype='text/plain')


def capture(request):
    '''Resource for capture data.'''

    proxy = get_proxy()

    description = {
        'label': ('string', 'Label'),
        'value': ('number', 'Value'),
        }

    # Retrieve statistics.
    data = None
    try:
        data = [
            {'label': 'Capture', 'value': proxy.capture(), },
            ]
    except Exception, e:
        data = [
            {'label': 'Capture', 'value': 0, },
            ]

    # Package as data table.
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)

    # Package as json and return.
    req_id = request.GET['tqx'].split(':')[1]
    json = data_table.ToJSonResponse(columns_order=('label', 'value'),
                                     order_by="label", req_id=req_id)
    return HttpResponse(str(json), mimetype='text/plain')
