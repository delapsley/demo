VDAS Demonstration Software
===========================

## Overview

This software was used to implement a simple monitoring application
to visualize a 16 Gbps VLBI demonstration given in June 2011.

The software consists of two components:

  * __monitor:__ a django-based application that uses google visualization
    API and jQuery to visualize the interface statistics for a Data
    Acquisition System.

  * __server:__ a simple python XML RPC server that retrieved data from the Data
    Acquisition System via an XML API and then published it via XML RPC.

The software was written in about half a day.

## Architecture

The figure below gives a high level view of the system.

The __main__ django view renders a template which includes javascript that
loads google viz components. These components then pull data from the __stats__
view via a (minimal) RESTful API.

The __stats__ view in turn uses XML RPC with calls to functions
*interface()*, *ethernet()*, and *capture()* to pull data from the
__StatsServer__.

The __StatsServer__ pulls data from the 16 Gbps Data Acquisition System using
XML over TCP.

![Architecture](https://raw.github.com/delapsley/demo/master/architecture.png)


## Installation

To install the software, follow these steps:

### Step 1. Install pre-requisites

    $ easy_install django

### Step 2. Clone demo repository

    $ git clone https://github.com/delapsley/demo.git

## Running the System in Simulation Mode

To run the system in simulation mode, follow these steps.

### Step 1. Start the StatsServer in Simulation mode

    $ cd server
    $ python StatsServer.py -F

### Step 2. Start the Django Server

In a separate terminal window, issue the following commands:

    $ cd monitor
    $ python manage.py runserver

### Step 3. View the monitoring page

Open your web browser at the following URL:

    http://127.0.0.1:8000/main/

You should see something that resembles the figure below.

![Architecture](https://raw.github.com/delapsley/demo/master/screenshot.png)

### Step 4. Enjoy!

Enjoy the application.

## Questions

Please email me, <delapsley@gmail.com> if you have any questions.

