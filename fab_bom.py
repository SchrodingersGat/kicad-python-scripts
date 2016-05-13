
from __future__ import print_function

import re
import csv
import sys
import os
import shutil

import argparse

DELIMITER = ","

sys.path.append(os.getcwd())

import bom_netlist_reader
import bomfunk_csv
from bomfunk_csv import CSV_DEFAULT as COLUMNS, CSV_IGNORE_FAB as IGNORE

global DEBUG
DEBUG = True

def debug(msg):
    global DEBUG
    if DEBUG == True:
        print(msg)

def close(msg=""):
    print(msg)
    sys.exit(0)

def error(msg=""):
    print(msg)
    sys.exit(-1)

#individual components
components = []

#component groups
groups = []

#get the input file (.xml)

parser = argparse.ArgumentParser()
parser.add_argument('net',help="KiCAD netlist file, .xml format",type=str,nargs=1)
args = parser.parse_args()

xml_file = args.net[0]

#xml_file = "C:\\Users\\Oliver\\Google Drive\\Reverse GeoCache Box\\PCB\\USB_Geocache.xml"

#convert to windows-style if needed
if (os.path.sep == '\\'):
    xml_file = xml_file.replace("/",os.path.sep)

print("File: " + xml_file)

if not os.path.isfile(xml_file):
    error(xml_file + " is not a file")

if not xml_file.endswith(".xml"):
    error(xml_file + " is not a .xml file")

#read out the netlist
net = bom_netlist_reader.netlist(xml_file)

#extract the components
components = net.getInterestingComponents()

#group the components
groups = net.groupComponents(components)
   
#now, look for a corresponding .csv file (does it exist?)
csv_file = xml_file.replace(".xml","_fab.csv")

###Re-load in the CSV values (if they match!)
if (os.path.exists(csv_file)) and (os.path.isfile(csv_file)):

    lines = []

    rows = bomfunk_csv.getRows(csv_file)

    for row in rows:
        for group in groups:
            if group.compareCSVLine(row):
                group.csvFields = row
                break

#write out the datas
if bomfunk_csv.saveRows(csv_file, groups, net.getSource(), net.getVersion(), net.getDate(), ignore=IGNORE, ignoreDNF=False) == True:
    close("Complete - saved data to " + csv_file)
else:
    close("Error writing to " + csv_file + ". Is it open?")
    
