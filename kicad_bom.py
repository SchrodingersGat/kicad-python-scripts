
from __future__ import print_function

import re
import csv
import sys
import os
import shutil

import argparse

DELIMITER = ","

sys.path.append(os.getcwd())

import kicad_netlist_reader
from kicad_netlist_reader import CSV_COLUMNS as COLUMNS

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
net = kicad_netlist_reader.netlist(xml_file)

#extract the components
components = net.getInterestingComponents()

#group the components
groups = net.groupComponents(components)
   
#now, look for a corresponding .csv file (does it exist?)
csv_file = xml_file.replace(".xml",".csv")

###TODO

###Re-load in the CSV values (if they match!)

if (os.path.exists(csv_file)) and (os.path.isfile(csv_file)):

    lines = []

    with open(csv_file,'r') as csv_read:
        reader = csv.reader(csv_read, delimiter=DELIMITER, lineterminator='\n')
        
        debug("Reading from " + csv_file)
        
        for line in reader:
            lines.append(line)
            
    if len(lines) > 0:
            
        #read out the headings
        headings = lines[0]
        
        row = {}
        
        for line in lines[1:]:
            #dict the row data
            row = dict(zip(headings,line))
            
            #try to match groups
            for g in groups:
                if g.compareCSVLine(row) == True:
                
                    #back-copy the CSV data
                    g.addCSVLine(row)
            
    #make a temporary copy
    shutil.copyfile(csv_file,csv_file + ".tmp")
            
#write out the datas
with open(csv_file,"w") as csv_write:
    writer = csv.writer(csv_write, delimiter=DELIMITER, lineterminator='\n')
    
    #write the columns
    writer.writerow(COLUMNS)
    
    #look the the groups
    for group in groups:
                
        if group.getCount() == 0: continue
        
        writer.writerow(group.getRow(COLUMNS))
        
    #write out some blank rows
    for i in range(2):
        writer.writerow([])
        
    #write out the TOTAL column
    #(start with 'details' info))
    total = [""] * 9 + ["Total:",str(len(net.components))]
    
    writer.writerow(total)
    
    for i in range(5):
        writer.writerow([])
        
    #write out version info
    
    #add extra data to the bottom of the file
    writer.writerow(['Component Count:', len(net.components)])
    writer.writerow(['Source:', net.getSource()])
    writer.writerow(['Version:',net.getVersion()])
    writer.writerow(['Date:', net.getDate()])
    writer.writerow(['Tool:', net.getTool()])

close("Complete")