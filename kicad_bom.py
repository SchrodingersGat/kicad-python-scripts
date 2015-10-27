#KiCAD BOM Generation script

#Usage:
#python "path/to/script" "%I" "%O"

from __future__ import print_function

import re
import csv
import sys
import os

sys.path.append(os.getcwd())

def debug(s):
        DEBUG = True
        if (DEBUG == True):
                print(s)

def close(msg):
        print(msg)
        sys.exit(0)

"""
    @package
    Generate a Tab delimited list (csv file type).
    Components are sorted by ref and grouped by value
    Fields are (if exist)
    'Ref', 'Qnty', 'Value', 'Sch lib name', 'footprint', 'Description', 'Vendor'
"""

#'better' sorting function which sorts by NUMERICAL value not ASCII
def natural_sort(string):
	return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)',string)]

# Import the KiCad python helper module and the csv formatter
import kicad_netlist_reader

args = sys.argv

xml_file = args[1]

if not xml_file.endswith(".xml"):
    close(xml_file + " is not a .xml file")

debug("Netlist file: " + xml_file)
    
# Generate an instance of a generic netlist, and load the netlist tree from
# the command line option. If the file doesn't exist, execution will stop
net = kicad_netlist_reader.netlist(xml_file)

output_file = xml_file.replace(".xml",".csv")

debug("Saving BOM to:")
debug(output_file)

###Extra fields to search for and add the info to the BOM
EXTRA_FIELDS = ["Notes","Manufacturer","Part Number","Vendor","Alt Vendor"]

# Open a file to write to, if the file cannot be opened output to stdout
# instead
try:
    f = open(output_file, 'w')
except IOError:
    e = "Can't open output file for writing: " + sys.argv[2]
    print(__file__, ":", e, sys.stderr)
    f = sys.stdout

try: #main try block (catch all errors)
	
	# Create a new csv writer object to use as the output formatter
	out = csv.writer(f, lineterminator='\n', delimiter='\t') #, quotechar='\"',quoting=csv.QUOTE_NONE)

	row = ["Description","References","Value","Footprint"]
	
	for field in EXTRA_FIELDS:
		row.append(field)
		
	row.append("Quantity")
	row.append("Unit Price")
	row.append("Cost Per Board")
	
	#write the headers
	out.writerow(row)

	# Get all of the components in groups of matching parts + values
	# (see ky_generic_netlist_reader.py)
	#grouped = net.groupComponents()

	components = net.getInterestingComponents()
	
	numComponents = len(components)
	
	grouped = net.groupComponents(components)
		
	try:
		for i in range(len(grouped)):
			group = grouped[i]
			#use a much better sorting algorhythm
			group = sorted(group, key = lambda g: natural_sort(g.getRef()))
			grouped[i] = group
	except:
		debug ("Unexpected Error: " + str(sys.exc_info()[1]))
		raw_input()
			
	# Output all of the component information
	for group in grouped:

		refs = ""

		###Extra fields that are supported by this script
		fields = [""] * len(EXTRA_FIELDS)
		
		# Add the reference of every component in the group and keep a reference
		# to the component so that the other data can be filled in once per group
		for component in group:
			refs += component.getRef() + ", "
			c = component
			
			fieldInfo = ""
			
			for i,field in enumerate(EXTRA_FIELDS):
				try:
					fieldInfo = c.getField(field)
					
					if (fieldInfo == ""): pass
					else:
						#if blank, set it!
						if (fields[i] == ""): fields[i] = fieldInfo
						elif (fields[i] == fieldInfo): pass
						else:
							fields[i] = fields[i] + ", " + fieldInfo #append new data
				except:
					pass



		##delete thr trailing comma
		if len(refs) > 0:
			refs = refs[:-2]

			row = [c.getDescription(), refs, c.getValue(), c.getFootprint().split(":")[-1]]

			for field in fields:
				row.append(field)

			row.append(len(group)) #number of components
			
			out.writerow(row)

	#add extra data to the bottom of the file
	out.writerow([])
	out.writerow([])
	out.writerow([])
	out.writerow(['Source:', net.getSource()])
	out.writerow(['Date:', net.getDate()])
	out.writerow(['Tool:', net.getTool()])
	out.writerow(['Component Count:', len(net.components)])
			
			
	
except:
	debug("Error - " + str(sys.exc_info()[1]))

try:		
	f.close()
	debug("Generated BOM for " + str(numComponents) + " components.")
except:
	pass
