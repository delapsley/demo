# Create your views here.
import re
import socket
import gviz_api
import time
import random
import socket

from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render_to_response
from xml.dom.minidom import Document
from django.conf import settings
from xmlrpclib import ServerProxy
from xml.etree.ElementTree import fromstring

SOCKET_TIMEOUT = 2

def interface(request):

    try:
        proxy = ServerProxy('http://localhost:9000/')
        socket.setdefaulttimeout(SOCKET_TIMEOUT)
    except Exception, e:
        print 'Connect timeout: %s'%e

    description = {
        'interface': ('string', 'Interface'),
        'byteCount': ('number', 'byteCount'),
        'bytesDropped': ('number', 'bytesDropped'),
        'packetCount': ('number', 'packetCount'),
        'packetsDropped': ('number', 'packetsDropped'),
        'errorCount': ('number', 'errorCount'),
        }

    data = []
    labels = [ 'interface', 'byteCount', 'bytesDropped', 'packetCount', 'packetsDropped', 'errorCount' ]

    try:
        for i in range(4):
            data.append( dict(zip(labels, [ int(x) for x in proxy.interface(str(i)) ])))
    except Exception, e:
        print 'Data timeout: %s'%e
        for i in range(4):
            data.append(dict(zip(labels, [ 0 for x in range(len(labels)) ])))

    print 'DATA', data

    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)

    req_id = request.GET['tqx']
    req_id = req_id.split(':')[1]
    json = data_table.ToJSonResponse(columns_order=('interface', 'byteCount', 'bytesDropped',
                                                    'packetCount', 'packetsDropped', 'errorCount'),
                                    req_id=req_id)
    return HttpResponse(str(json), mimetype='text/plain')


def ethernet(request):

    try:
        proxy = ServerProxy('http://localhost:9000/')
        socket.setdefaulttimeout(SOCKET_TIMEOUT)
    except Exception, e:
        print 'Connect timeout: %s'%e

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

    print 'ETHERNET', data

    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)
    req_id = request.GET['tqx']
    req_id = req_id.split(':')[1]
    json = data_table.ToJSonResponse(columns_order=('label', 'value'),
                                     order_by="label", req_id=req_id)
    return HttpResponse(str(json), mimetype='text/plain')


def capture(request):

    try:
        proxy = ServerProxy('http://localhost:9000/')
        socket.setdefaulttimeout(SOCKET_TIMEOUT)
    except Exception, e:
        print 'Connect timeout: %s'%e

    description = {
        'label': ('string', 'Label'),
        'value': ('number', 'Value'),
        }

    data = None

    try:
        data = [
            {'label': 'Capture', 'value': proxy.capture(), },
            ]
    except Exception, e:
        data = [
            {'label': 'Capture', 'value': 0, },
            ]

    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)
    req_id = request.GET['tqx']
    req_id = req_id.split(':')[1]
    json = data_table.ToJSonResponse(columns_order=('label', 'value'),
                                     order_by="label", req_id=req_id)
    print json
    return HttpResponse(str(json), mimetype='text/plain')
