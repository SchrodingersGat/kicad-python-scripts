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

#Extract input file and output dir information
if len(args) < 2: 
    #close("Not enough arguments supplied to script")
    xml_file = "C:\\Users\\Oliver\\Google Drive\\Reverse GeoCache Box\\PCB\\USB_Geocache.xml"
else:
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

	#Data headers
	out.writerow([
					'Description',
					'Notes',
					'References', 
					'Value',
#					'KiCAD Library Name',
					'Footprint',
					'Manufacturer',
					'Part Number',
					'Vendor',
					'Vendor Code',
					'Quantity'
					])

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

		vendor = ""
		vendorPartNumber = ""
		
		altVendor = ""
		altVendorPartNumber = ""
		
		manu = ""
		manuPartNumber = ""
		
		notes = ""
		

		# Add the reference of every component in the group and keep a reference
		# to the component so that the other data can be filled in once per group
		for component in group:
			refs += component.getRef() + ", "
			c = component
			
			try:
				partNotes = c.getField("Notes")
				if (partNotes == ""):
					pass
				else:
					if (notes == ""):
						notes = partNotes
					elif (notes == partNotes):
						pass
					else:
						notes = notes +", " + partNotes
			except:
				pass
			
			#Extract the vendor (supplier) info
			try:
				vendorString = c.getField("Vendor")
				if (vendorString == ""): 
					pass
				else:
					vs = vendorString.split(":")
					if len(vs) == 2: # "Vendor:VendorPartNumber"
						if (vendor == ""): # no vendor already supplied
							vendor = vs[0]
						
						if (vendorPartNumber == ""): #no vpn already supplied
							vendorPartNumber = vs[1]
					elif len(vs) == 1: # "vendor"
						if (vendorPartNumber == ""): # no vendor already supplied
							vendorPartNumber = vs[0]
			except:
				pass
				
				
			##extract the manufacturer:partnumber info
			try:
				manuString = c.getDatasheet()
				
				ms = manuString.split(":")
				
				if len(ms) == 2: # "Manufacturer:ManufacturerPartNumber"
					if (manu == ""):
						manu = ms[0]
					if manuPartNumber == "":
						manuPartNumber = ms[1]
				elif len(ms) == 1: # "ManufacturerPartNumber"
					if (manuPartNumber == ""):
						manuPartNumber = ms[0]
				
			except: 
				pass
		##delete thr trailing comma
		if len(refs) > 0:
			refs = refs[:-2]
		
			
		# Fill in the component groups common data
		out.writerow([
					c.getDescription(),	
					notes,
					refs,
					c.getValue(),
					#c.getLibName() + "/" + c.getPartName(),
					c.getFootprint().split(":")[-1],
					manu, #manufacturer
					manuPartNumber, #"", #manufacturer part number
					vendor, #"", #supplier
					vendorPartNumber, #supplier code
					len(group)
					])
					
	#    out.writerow([refs, len(group), c.getValue(), c.getLibName() + "/" + c.getPartName(), c.getFootprint(),
	#        c.getDescription(), c.getField("Vendor")])

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
	
	
raw_input("Done. Press <Enter> to close")
