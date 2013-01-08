#!/usr/bin/env python

#------------------------------------------------------------------------------
# Date: 1/7/2013
# Author:   delapsley@gmail.com
# Description:
#
#   Simple stats server implemented for a VDAS demonstration. This server
#   reads data from a data acquisition system via an XML interface and then
#   publishes it via XMLRPC.
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
from copy import copy
from threading import Thread
from xml.etree.ElementTree import fromstring
from SimpleXMLRPCServer import SimpleXMLRPCServer

#------------------------------------------------------------------------------
# Globals
#------------------------------------------------------------------------------

# Command to be sent to logging system.
GET_STATS_CMD='''<x3c_cmd><cmdName>get stats</cmdName></x3c_cmd>'''

# RE for response from logging system.
RESPONSE_RE = re.compile('(<cmd_resp>.*</cmd_resp>)')


def parse_stats(s):
    '''Parse XML response from logging system.

    :param s: XML string to be parsed.
    :returns: a list of interface statistic vectors.
        Each vector contains the following:
            [
                byteCount,
                bytesDropped,
                packetCount,
                packetsDropped,
                errorCount,
            ].'''
    root = fromstring(s)
    interfaces = dict()

    # Loop through all params and collect interface info.
    current_interface = None
    for p in root.findall('param'):
        if cmp(p.findtext('name'), 'interfaceNumber') == 0:
            if current_interface is not None:
                # Add the current interface to the interfaces dict.
                interfaces[current_interface[0]] = current_interface

            # Create a new interface stats vector.
            current_interface = [0, 0, 0, 0, 0, 0]
            current_interface[0] = p.findtext('value')

        # Update the interface stats vector.
        if current_interface is not None:
            if cmp(p.findtext('name'), 'byteCount') == 0:
                current_interface[1] = int(p.findtext('value'))

            elif cmp(p.findtext('name'), 'bytesDropped') == 0:
                current_interface[2] = int(p.findtext('value'))

            elif cmp(p.findtext('name'), 'packetCount') == 0:
                current_interface[3] = int(p.findtext('value'))

            elif cmp(p.findtext('name'), 'packetsDropped') == 0:
                current_interface[4] = int(p.findtext('value'))

            elif cmp(p.findtext('name'), 'errorCount') == 0:
                current_interface[5] = int(p.findtext('value'))

    interfaces[current_interface[0]] = current_interface

    # Return the list of stats vectors.
    return interfaces


#------------------------------------------------------------------------------
# Class definitions
#------------------------------------------------------------------------------
class FakeData(object):
    '''Generate fake acquisition system data.'''


    # Static fake data tags and templates.
    FAKE_START_TAG = '''<cmd_resp>'''
    FAKE_END_TAG = '''</cmd_resp>'''
    FAKE_HEADER = string.Template('''
        <cmd_name>get stats</cmd_name>
        <retVal>0</retVal>
        <reason>success</reason>
        <param>
          <name>interfaceCount</name><type>unsigned</type><value>${num_interfaces}</value>
        </param>''')

    FAKE_BODY = string.Template('''
        <param>
          <name>interfaceType</name><type>keyword</type><value>Ethernet</value>
        </param>
        <param>
          <name>interfaceNumber</name><type>unsigned</type><value>${int_id}</value>
        </param>
        <param>
          <name>byteCount</name><type>unsigned long</type><value>${byte_count}</value>
        </param>
        <param>
          <name>bytesDropped</name><type>unsigned long</type><value>${bytes_dropped}</value>
        </param>
        <param>
          <name>packetCount</name><type>unsigned long</type><value>${packet_count}</value>
        </param>
        <param>
          <name>packetsDropped</name><type>unsigned long</type><value>${packets_dropped}</value>
        </param>
        <param>
          <name>errorCount</name><type>unsigned long</type><value>${error_count}</value>
        </param>''')

    # List of keys that will be updated.
    STAT_KEYS = ['byte_count', 'bytes_dropped', 'packet_count',
        'packets_dropped', 'error_count']

    # Useful constants.
    BYTE_INCREMENT = 1000000000
    PACKET_INCREMENT = BYTE_INCREMENT/8000

    def __init__(self, num_interfaces=4):
        '''Constructor.

        :param num_interfaces: the number of interfaces.'''
        self.num_interfaces = num_interfaces

        # Initialize interfaces dict.
        self.interfaces = [{'int_id': x} for x in xrange(self.num_interfaces)]

        # Initialize interfaces statistics.
        for i in xrange(self.num_interfaces):
            for k in FakeData.STAT_KEYS:
                self.interfaces[i][k] = 0

    def update_interface(self, int_id, byte_count, bytes_dropped, packet_count,
        packets_dropped, error_count):
        '''Update the statistics on an interface.

        :param int_id: interface identifier/index.
        :param byte_count: total byte count so far.
        :param bytes_dropped: total bytes dropped so far.
        :param packet_count: total packet count so far.
        :param packets_dropped: total packets dropped so far.
        :param error_count: errors seen so far.'''
        if int_id < 0 or int_id >= self.num_interfaces:
            raise 'Invalid interface id: %d' % int_id

        # Update the interface statistics.
        for k in FakeData.STAT_KEYS:
            self.interfaces[int_id][k] += locals()[k]

    def __str__(self):
        '''Returns new statistic XML string for parsing.'''
        for i in xrange(self.num_interfaces):
            bc = random.randint(0, FakeData.BYTE_INCREMENT)
            bd = random.randint(0, FakeData.BYTE_INCREMENT)
            pc = random.randint(0, FakeData.PACKET_INCREMENT)
            pd = random.randint(0, FakeData.PACKET_INCREMENT)
            ec = random.randint(0, FakeData.PACKET_INCREMENT)
            self.update_interface(i, bc, bd, pc, pd, ec)

        xml_body = [FakeData.FAKE_START_TAG]
        xml_body.append(FakeData.FAKE_HEADER.substitute({'num_interfaces':
                                                         self.num_interfaces}))

        for i in xrange(self.num_interfaces):
            xml_body.append(FakeData.FAKE_BODY.substitute(self.interfaces[i]))

        xml_body.append(FakeData.FAKE_END_TAG)

        return ''.join(xml_body)


class StatsServer(SimpleXMLRPCServer):
    '''This class customizes the default SimpleXMLRPCServer.'''


    def __init__(self, polling_interval, address_tuple, target, fake=False):
        '''Constructor.

        :param polling_interval: how frequently to poll.
        :param address_tuple: the tuple (<ip address>, <port>).
        :param target: the target logging system.
        :param fake: whether or not to generate fake data.'''
        SimpleXMLRPCServer.__init__(self, address_tuple)

        self._polling_interval = polling_interval
        if polling_interval < 1:
            self._polling_interval = 1

        self._target = target
        self._fake = fake
        self._running = False

        self._last_update = time.time()
        self._rates = dict()
        self._capture_rate = 0
        self._cstatistics = dict()

        # Register external API handlers.
        self.register_introspection_functions()
        self.register_function(self.interface)
        self.register_function(self.ethernet)
        self.register_function(self.capture)

    def start(self):
        '''Start the server.'''
        self._running = True
        self._stats_thread = Thread(target=lambda: self.run())
        self._stats_thread.start()
        self._start_time = time.time()

    def server_bind(self):
        '''Ensure TCP resources released immediately if server killed.'''
        import socket
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        SimpleXMLRPCServer.server_bind(self)

    def serve(self):
        '''Service requests until quit() called.'''
        while self._running:
            self.handle_request()

    def running(self):
        '''Return whether or not server is running.'''
        return self._running

    def quit(self):
        '''Shutdown server.'''
        self._running = False
        return 0

    def run(self):
        '''Main execution loop.

        Two options for running.'''
        if self._fake:
            self._fake_run()
        else:
            self._run()

    def _run(self):
        '''Acquire and publish real data.'''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(self._target)

        print '** Connected'
        while self._running:
            s.sendall(GET_STATS_CMD)
            received_data = []
            try:
                # Command loop
                while True:
                    data = s.recv(1)
                    data = data.strip()
                    received_data.append(data)
                    received_string = ''.join(received_data)
                    m = re.match(RESPONSE_RE, received_string)
                    if m:
                        received_response, = m.groups(0)
                        now = time.time()
                        delta_t = now - self._last_update
                        interfaces = parse_stats(received_response)

                        for i, V in interfaces.iteritems():
                            try:
                                if not self._cstatistics.has_key(str(i)):
                                    self._cstatistics[i] = list(V)
                                    continue

                                self._rates[i] = 0
                                delta_v = int(V[1]) - int(self._cstatistics[str(i)][1])
                                self._cstatistics[str(i)][1] = V[1]
                                self._rates[i] = float(delta_v)/delta_t
                            except Exception, e:
                                print 'STATS LOOP:', str(e)

                        self._capture_rate = 0
                        for i, v in self._rates.iteritems():
                            self._capture_rate += v

                        self._last_update = time.time()
                        print 'STATS', self._rates
                        break

                time.sleep(self._polling_interval)
            except Exception, e:
                print '** Shutting down'
                self.quit()
                self.shutdown()

        s.close()

    def _fake_run(self):
        '''Publish fake data.'''
        print '** Connected'
        fd = FakeData()

        while self._running:
            received_data = str(fd)
            try:
                # Command loop
                now = time.time()
                delta_t = now - self._last_update
                interfaces = parse_stats(received_data)

                for i, V in interfaces.iteritems():
                   try:
                       if not self._cstatistics.has_key(str(i)):
                           self._cstatistics[i] = list(V)
                           continue

                       self._rates[i] = 0
                       delta_v = int(V[1]) - int(self._cstatistics[str(i)][1])
                       self._cstatistics[str(i)][1] = V[1]
                       self._rates[i] = float(delta_v)/delta_t
                   except Exception, e:
                       print 'STATS LOOP:', str(e)

                self._capture_rate = 0
                for i, v in self._rates.iteritems():
                   self._capture_rate += v

                self._last_update = time.time()
                print 'STATS', self._rates

                time.sleep(self._polling_interval)
            except Exception, e:
                print '** Shutting down: %s' %e
                self.quit()
                self.shutdown()

    def join(self):
        self._stats_thread.join()

    def interface(self, id_):
        '''Return interface statistics.

        :param id_: the interface being queried.'''
        print self._cstatistics[id_]
        return [ str(x) for x in self._cstatistics[id_] ]

    def ethernet(self, id_):
        '''Return ethernet statistics.

        :param id_: the interface being queried.'''
        if self._rates.has_key(id_):
            raw_rate = self._rates[id_]*8/1000000000.0
            return round(raw_rate,1)

        return 0

    def capture(self):
        '''Return capture statistics.'''
        raw_rate = self._capture_rate*8/1000000000.0
        return round(raw_rate,1)

def usage():
    print '''
usage: statsserver -l <logger host>
                   -p <logger port>
                   -b <bind port>
                   -i <polling interval(s)>
                   -F   generate fake data
                   -h   print this message.
'''

#------------------------------------------------------------------------------
# Main program
#------------------------------------------------------------------------------
if __name__ == '__main__':
    # Configuration variables with their defaults.
    LOGGER_PORT = 6050
    BIND_PORT = 9000
    LOGGER_HOST = 'localhost'
    POLLING_INTERVAL = 5
    FAKE = False

    # Parse command line options.
    OPTIONS = 'l:p:b:i:hF'
    try:
        opts, args = getopt.getopt(sys.argv[1:], OPTIONS)
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)

    for o, a in opts:
        if o == '-l':
            LOGGER_HOST = a
        elif o == '-p':
            LOGGER_PORT = int(a)
        elif o == '-b':
            BIND_PORT = int(a)
        elif o == '-i':
            POLLING_INTERVAL = int(a)
        elif o == '-F':
            FAKE = True
        elif o == '-h':
            usage()
            sys.exit(2)
        else:
            usage()
            assert False, 'Unhandled option: %s'%str(o)

    # Instantiate and start the server.
    s = StatsServer(POLLING_INTERVAL, ('localhost', BIND_PORT),
                    (LOGGER_HOST, LOGGER_PORT), FAKE)
    s.start()
    s.serve_forever()

