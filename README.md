VDAS Demonstration Software
===========================

This software was used to implement a simple monitoring application
to visualize a 16 Gbps VLBI demonstration given in June 2011.

The software consists of two components:

  * __monitor:__ a django-based application that uses google visualization
    API and jQuery to visualize the interface statistics for a Data
    Acquisition System.

  * __server:__ a simple python XML RPC server that retrieved data from the Data
    Acquisition System via an XML API and then published it via XML RPC.

The software was written in about half a day.
