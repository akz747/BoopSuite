#!/usr/bin/env python

# Notes:
#    TODO:
#        FILTER BY MAC ADDRESS! FINAL PART!!! HOPEFULLY

__author__  = 'Jarad Dingman';
__year__    = [2016, 2017];
__status__  = 'Testing';
__contact__ = 'kali.pentest.device@gmail.com';
__version__ = '12.0.0';

# Imports
import os
import sys
import signal
import logging

import Globals.MyGlobals as confg
import Handlers.probe_requests as probereq
import Handlers.probe_response as proberes
import Handlers.beacon as beacon
import Handlers.data as data
import Misc.misc as misc

# Configure Scapy
logging.getLogger('scapy.runtime').setLevel(logging.ERROR);

# From Imports
from Misc.printer import printer_thread
from Misc.hopper import channel_hopper
from Classes.classes import *
from scapy.all import *
from threading import Thread

# Scapy Restraint
conf.verb = 0;

# threads
def sniff_packets( packet ):
	#filter_address = "b0:10:41:88:bf:72"; if packet.addr1 == filter_address or packet.addr2 == filter_address:
	if packet[0].type == 0:
		if packet[0].subtype == 4:
			Thread_handler = Thread(target=probereq.handler_1, args=[packet[0]]).start();

	  	elif packet[0].subtype == 5 and packet[0].addr3 in confg.HIDDEN:
	  		Thread_handler = Thread(target=proberes.handler_2, args=[packet[0]]).start();

	 	elif packet[0].subtype == 8:
	  		Thread_handler = Thread(target=beacon.handler_3, args=[packet[0]]).start();

	elif packet[0].type == 2 and packet[0].addr1 not in confg.IGNORE and packet[0].addr2 not in confg.IGNORE:					# or packet[0].type == 4? Does packet type 4 exist?
	  	Thread_handler = Thread(target=data.handler_4, args=[packet[0]]).start();
	else:
		pass;

# MAIN CONTROLLER
def main(configuration):
    def signal_handler(*args):
        confg.FLAG = False;

        if configuration.__REPORT__ != False:
			wifis = list(map(get_aps, confg.APS));
			wifis.sort(key=lambda x: x[6]);
			wifis.remove(wifis[0]);

			clients = list(map(get_clients, confg.CLS));
			clients.sort(key=lambda x: x[4]);
			print("[+] Generating Report.");
			configuration.__REPORT__.write(tabulate(wifis, headers=['M', 'E', 'Ch', 'V', 'S', 'B', 'SS'], tablefmt="psql")+"\r\n");
			configuration.__REPORT__.write(tabulate(clients, headers=['M', 'AP M', 'N', 'S', 'AP'], tablefmt="psql")+"\r\n");
			configuration.__REPORT__.close();

        print("\r[+] Commit to Exit.");

        sys.exit(0);
        return;

    signal.signal(signal.SIGINT, signal_handler);
    # Initialize an empty Access Point for easier printing.
    confg.APS[""] = Access_Point('','','','','','');

    if configuration.__HOP__ == True:
        Hopper_Thread = Thread(target=channel_hopper, args=[configuration]).start();
    else:
        os.system('iwconfig ' + configuration.__FACE__ + ' channel ' + configuration.__CC__);

    if configuration.__PRINT__ == True:
        Printer_Thread = Thread(target=printer_thread, args=[configuration]).start();

    sniff(iface=configuration.__FACE__, prn=sniff_packets, store=0);

    return 0;

if __name__ == '__main__':
    misc.display_art();
    configuration = Configuration();
    configuration.parse_args();
    misc.set_size(51, 95);
    main(configuration);
