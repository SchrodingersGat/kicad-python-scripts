import csv
import os

"""
define standard CSV columns for BoM management
"""

#Standard CSV columns that will be printed
CSV_DEFAULT = ["Description","References","Value","Footprint","Rating","Manufacturer","Part Number","Vendor","Vendor Code","Alt. Vendor","Alt. Vendor Code","Quantity","Price","Cost Per Board","Notes","Datasheet","URL"]

#these columns are ALWAYS updated from the schematic netlist
CSV_PROTECTED = ["Description","References","Value","Footprint","Quantity"]

#these columns are used to match lines from a CSV file
CSV_MATCH = ["Description","Value","Footprint"]


def getRows(filename, header_row=0, delimiter=','):
    
    rows = []
    
    if (header_row < 0): header_row = 0
    
    if not os.path.exists(filename) or not os.path.isfile(filename): return rows
    if not filename.endswith(".csv"): return rows
    
    with open (filename,'r') as csv_read:
        reader = csv.reader(csv_read, delimiter=delimiter, lineterminator='\n')
        
        #extract the raw lines
        lines = [line for line in reader]
        
        if len(lines) <= header_row: return rows
        
        #drop leading rows
        lines = lines[header_row:]
        
        #read the header row
        headers = lines[0]
        
        lines = lines[1:]
        
        rows = [dict(zip(headers,line)) for line in lines]
        
        return rows
        
def saveRows(filename, groups, source, version, date, delimiter=','):
    
    if not filename.endswith(".csv"): return
    
    with open(filename,'w') as csv_write:
        
        writer = csv.writer(csv_write, delimiter=delimiter, lineterminator='\n')
        
        writer.writerow(CSV_DEFAULT)
        
        for group in groups:
            writer.writerow(group.getRow(CSV_DEFAULT))
            
        #write out extra data
        
        for i in range(5):
            writer.writerow([])
            
        writer.writerow(["Component Count:",len(groups)])
        writer.writerow(["Source:",source])
        writer.writerow(["Version:",version])
        writer.writerow(["Date:",date])
        
        return True
        
    return False
