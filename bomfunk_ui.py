from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import QFileDialog
import sys
import os

localDir = os.path.split(sys.argv[0])[0]

sys.path.append(os.getcwd())
sys.path.append(localDir)


from bomfunk_csv import CSV_DEFAULT as CSV_DEFAULT
from bomfunk_csv import CSV_PROTECTED as CSV_PROTECTED
from bomfunk_csv import CSV_MATCH as CSV_MATCH

import bomfunk_csv

import bomfunk_netlist_reader

#Cell Background Colors
def colorProtected():
    return QtGui.QColor(0xFF,0xCC,0xFF)

def colorNormal():
    return QtGui.QColor(0xFF,0xFF,0xFF)

def colorConflict():
    return QtGui.QColor(0xFF,0x66,0x00)

def colorCSV():
    return QtGui.QColor(0x66,0xFF,0x66)

def colorKiCAD():
    return QtGui.QColor(0x66,0xCC,0xFF)

class BOMWidget(QtGui.QMainWindow):

    def __init__(self, args=[]):
    
        super(BOMWidget, self).__init__()

        self.headings = CSV_DEFAULT
        self.csvFile = ""
        self.xmlFile = ""

        #kicad schematic info
        self.kicadSource = ""
        self.kicadVersion = ""
        self.kicadDate = ""
        self.kicadTool = ""

        self.reloading = False

        self.componentGroups = [] #Rows extracted from xml file (KiCAD netlist)
        self.csvRows = []         #Rows extracted from csv file

        self.initUI()

        self.handleArgs(args)

        self.show()

    def handleArgs(self, args):
        for arg in args:
            if self.xmlFile == "" and arg.endswith(".xml") and os.path.isfile(arg):
                self.xmlFile = arg
            if self.csvFile == "" and arg.endswith(".csv") and os.path.isfile(arg):
                self.csvFile = arg

        if self.xmlFile and not self.xmlFile == "":
            self.updateRows()

    def initUI(self):
        
        uic.loadUi(localDir + os.sep + "bomfunk.ui", self)

        self.setWindowTitle("BOMFunk KiCAD BOM Manager")

        self.updateHeadings()

        #connect SIGNALS/SLOTS
        QtCore.QObject.connect(self.action_loadCSV, QtCore.SIGNAL('triggered()'), self.loadCSV)
        QtCore.QObject.connect(self.action_loadXML, QtCore.SIGNAL('triggered()'), self.loadXML)
        QtCore.QObject.connect(self.action_saveCSV, QtCore.SIGNAL('triggered()'), self.saveCSV)

        QtCore.QObject.connect(self.table, QtCore.SIGNAL('cellChanged(int,int)'), self.cellDataChanged)

    def updateHeadings(self):
        self.table.setColumnCount(len(self.headings))
        self.table.setHorizontalHeaderLabels(self.headings)
        
    def loadCSV(self):

        fname = QFileDialog.getOpenFileName(
            None,
            "Load .csv BoM File",
            os.getcwd(),
            "CSV Files (*.csv)")

        #blank file
        if not fname: return

        fname = str(fname)

        if os.path.isfile(fname) and fname.endswith(".csv"):
            self.csvFile = fname

            #read out the rows
            rows = bomfunk_csv.getRows(fname)

            for row in rows:
                for group in self.componentGroups:
                    if group.compareCSVLine(row):
                        group.csvFields = row
                        break

            self.updateRows()

    def loadXML(self):

        fname = QFileDialog.getOpenFileName(
            None,
            "Load .xml KiCAD Netlist File",
            os.getcwd(),
            "XML Files (*.xml)")

        #blank file
        if not fname: return

        fname = str(fname)

        if os.path.isfile(fname) and fname.endswith(".xml"):
            self.xmlFile = fname
        else:
            return

        self.extractKicadData()

        self.updateRows()

    def saveCSV(self):

        if not self.csvFile or not os.path.isfile(self.csvFile) or not self.csvFile.endswith(".csv"):

            fname = str(QFileDialog.getSaveFileName(
                None,
                "Save .csv BoM File",
                os.getcwd(),
                "CSV Files (*.csv)"))

            if not fname:
                return False

            if fname.endswith(".csv"):
                self.csvFile = fname
            else:
                return False

        return bomfunk_csv.saveRows(fname, self.componentGroups, self.kicadSource, self.kicadVersion, self.kicadDate)

    def updateRows(self):

        self.reloading = True
        
        self.updateHeadings()
        
        self.table.setRowCount(len(self.componentGroups))

        for row,group in enumerate(self.componentGroups):
            for col,heading in enumerate(self.headings):

                item = self.table.item(row,col)

                if item == 0 or not item:
                    item = QtGui.QTableWidgetItem()

#                print("Heading:",heading,group.getField(heading))
                kicadData = group.getField(heading)
                csvData = group.getCSVField(heading)

                data = "" #actual data to be displayed

                if heading in CSV_PROTECTED:
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                    item.setBackgroundColor(colorProtected())
                    data = kicadData
                else:
                    
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
                    item.setBackgroundColor(colorNormal())

                    if kicadData == "" and csvData == "": #no data exists
                        pass
                    elif kicadData == "": #no KiCAD data
                        data = csvData
                        item.setBackgroundColor(colorCSV())
                    elif csvData == "": #no CSV data
                        data = kicadData
                        item.setBackgroundColor(colorKiCAD())
                    elif csvData == kicadData: #data matches!
                        data = kicadData
                    else: #conflict! (use KiCAD data in preference)
                        data = kicadData
                        print("Conflict:",data,csvData)
                        item.setBackgroundColor(colorConflict())

                item.setText(data)
                self.table.setItem(row,col,item)

        self.reloading = False

    def extractKicadData(self):

        if not self.xmlFile or self.xmlFile == "": return

        net = bomfunk_netlist_reader.netlist(self.xmlFile)

        if not net: return

        components = net.getInterestingComponents()

        self.componentGroups = net.groupComponents(components)

        self.kicadSource = net.getSource()
        self.kicadVersion = net.getVersion()
        self.kicadDate = net.getDate()
        self.kiacdTool = net.getTool()

    def cellDataChanged(self,row,col):

        if self.reloading: return
        print("Cell",row,col,"edited")
                        

def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = BOMWidget(sys.argv)
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()
    
