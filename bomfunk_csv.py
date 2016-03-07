import csv
import os
import shutil


"""
define standard CSV columns for BoM management
"""

#Standard CSV columns that will be printed
CSV_DEFAULT = ["Part","Description","References","Value","Footprint","Rating","Manufacturer","Part Number","Vendor","Vendor Code","Alt. Vendor","Alt. Vendor Code","Quantity","Price","Cost Per Board","Notes","Datasheet","URL"]

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
        
def saveRows(filename, groups, source, version, date, headings = CSV_DEFAULT, numberRows = True, delimiter=','):
    
    if not filename.endswith(".csv"): return

    #first, save a temporary copy of any old file (in case something goes wrong)
    if (os.path.exists(filename) and os.path.isfile(filename)):
        shutil.copyfile(filename, filename + ".tmp")

    try:
    
        with open(filename,'w') as csv_write:
            
            writer = csv.writer(csv_write, delimiter=delimiter, lineterminator='\n')

            if (numberRows == True):
                writer.writerow(["ID"] + headings)
            else:
                writer.writerow(headings)

            componentCount = 0
            
            for i,group in enumerate(groups):
                #CSV data is harmonized with KiCAD data
                #KiCAD data takes preference

                row = group.getHarmonizedRow(headings)

                if (numberRows == True):
                    row = [str(i+1)] + row

                writer.writerow(row)

                componentCount += group.getCount()
                
            #write out extra data
            
            for i in range(5):
                writer.writerow([])


            writer.writerow(["Component Count:",componentCount])
            writer.writerow(["Component Groups:",len(groups)])
            writer.writerow(["Source:",source])
            writer.writerow(["Version:",version])
            writer.writerow(["Date:",date])
            
            return True

    except BaseException as e:
        print(str(e))
    
    return False
