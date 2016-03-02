from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QApplication
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeyEvent, QKeySequence
import sys
import os

from bomfunk_csv import CSV_DEFAULT as CSV_DEFAULT
from bomfunk_csv import CSV_PROTECTED as CSV_PROTECTED
from bomfunk_csv import CSV_MATCH as CSV_MATCH

import bomfunk_csv

import bomfunk_netlist_reader

global UI_DEBUG
UI_DEBUG = True

def debug(*args):
    global UI_DEBUG
    if (UI_DEBUG):
        print(" ".join(str(i) for i in args))

ui_path = os.path.join(os.path.dirname(sys.argv[0]),"bomfunk.ui")

#Cell Background Colors
def colorProtected():
    return QtGui.QColor(0xFF,0xD6,0xCC)

def colorNormal():
    return QtGui.QColor(0xFF,0xFF,0xFF)

def colorConflict():
    return QtGui.QColor(0xFF,0x66,0x00)

def colorCSV():
    return QtGui.QColor(0xCC,0xFF,0xCC)

def colorKiCAD():
    return QtGui.QColor(0x66,0xCC,0xFF)

def colorError():
    return QtGui.QColor(0xCC,0xE6,0xFF)

class BOMWidget(QMainWindow):

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
                debug("Passed XML File:",self.xmlFile)
            if self.csvFile == "" and arg.endswith(".csv") and os.path.isfile(arg):
                self.csvFile = arg
                debug("Passed CSV File:",self.csvFile)

        if self.xmlFile == "" and not self.csvFile == "":
            self.xmlFile = self.csvFile.replace(".csv",".xml")
            debug("Trying XML File:", self.xmlFile)
            
        if not self.xmlFile == "":

            if self.csvFile == "":
                self.csvFile = self.xmlFile.replace(".xml",".csv")
                debug("Trying CSV File:",self.csvFile)
            
            self.extractKicadData()
            self.loadCSVFile(self.csvFile)
            self.updateRows()

    def initUI(self):

        uic.loadUi(ui_path, self)

        self.setWindowTitle("BOMFunk KiCAD BOM Manager")

        self.updateHeadings()

        #connect SIGNALS/SLOTS
        self.action_loadCSV.triggered.connect(self.loadCSV)

        self.action_loadXML.triggered.connect(self.loadXML)
        self.action_loadXML.shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        self.action_loadXML.shortcut.activated.connect(self.loadXML)

        self.action_saveCSV.triggered.connect(self.saveCSV)

        #shortcut for saving CSV file
        self.action_saveCSV.shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.action_saveCSV.shortcut.activated.connect(self.saveCSV)

        self.action_saveNewCSV.triggered.connect(self.saveCSVAs)
        self.action_saveNewCSV.shortcut = QShortcut(QKeySequence("Ctrl+Shift+S"),self)
        self.action_saveNewCSV.shortcut.activated.connect(self.saveCSVAs)

        self.table.cellChanged.connect(self.cellDataChanged)

        #close events
        self.action_exit.triggered.connect(self.close)

    def updateHeadings(self):
        self.table.setColumnCount(len(self.headings))
        self.table.setHorizontalHeaderLabels(self.headings)
        
    def loadCSV(self):

        fname, filter = QFileDialog.getOpenFileName(
            None,
            "Load .csv BoM File",
            os.getcwd(),
            "CSV Files (*.csv)")

        self.loadCSVFile(self,fname)

    def loadCSVFile(self, fname):

        debug("Loading CSV data from",fname)
        #blank file
        if not fname or str(fname)=="": return

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

        fname, filter = QFileDialog.getOpenFileName(
            None,
            "Load .xml KiCAD Netlist File",
            os.getcwd(),
            "XML Files (*.xml)")

        self.loadXMLFile(fname)

    def loadXMLFile(self, fname):

        debug("Loading XML data from",fname)
        #blank file
        if not fname or str(fname) == "":
            debug("XML file invalid")
            return

        if os.path.isfile(fname) and fname.endswith(".xml"):
            self.xmlFile = fname
        else:
            return

        self.extractKicadData()

        self.updateRows()

    def saveCSVAs(self):

        if self.getNewCSVFile():
            self.writeCSVFile()

    def getNewCSVFile(self):

        fname, filter = QFileDialog.getSaveFileName(
                None,
                "Save .csv BoM File",
                os.getcwd(),
                "CSV Files (*.csv)")

        if not fname or fname == "":
            return False

        if fname.endswith(".csv"):
            self.csvFile = fname
        else:
            return False

    def saveCSV(self):

        if not self.csvFile or not self.csvFile.endswith(".csv"):

            if self.getNewCSVFile():
                self.writeCSVFile()

        else:
            self.writeCSVFile()

    def writeCSVFile(self):

        debug("Writing CSV data to",self.csvFile)

        result = bomfunk_csv.saveRows(self.csvFile, self.componentGroups, self.kicadSource, self.kicadVersion, self.kicadDate)

        if result:
            debug("CSV Data Write OK")
        else:
            debug("Error writing CSV data")
        return result

    def updateRows(self):

        self.reloading = True
        
        self.updateHeadings()
        
        self.table.setRowCount(len(self.componentGroups))

        for row,group in enumerate(self.componentGroups):
            for col,heading in enumerate(self.headings):

                item = self.table.item(row,col)


                if item == 0 or not item:
                    item = QtWidgets.QTableWidgetItem()
                    self.table.setItem(row,col,item)

                #clear tool tip by default
                item.setToolTip("")

                kicadData = group.getField(heading)
                csvData = group.getCSVField(heading)

                data = "" #actual data to be displayed

                if heading in CSV_PROTECTED:
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                    item.setToolTip("Data in " + heading + " column cannot be edited")
                    if kicadData == "":
                        item.setBackground(colorError())
                    else:
                        item.setBackground(colorProtected())
                    data = kicadData
                else:

                    item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)

                    #default color
                    item.setBackground(colorNormal())

                    #KiCAD data takes preference!
                    if not kicadData == "":
                        data = kicadData
                        item.setBackground(colorKiCAD())

                        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)

                        item.setToolTip(heading + " field exists for part. Cannot be edited")
                    elif not csvData == "": #Data already exists in CSV File
                        item.setBackground(colorCSV())
                        data = csvData
                    else:
                        data = ""

                item.setText(data)

        self.reloading = False

    def extractKicadData(self):

        if not self.xmlFile or self.xmlFile == "": return

        debug("Loading XML data from",self.xmlFile)

        net = bomfunk_netlist_reader.netlist(self.xmlFile)

        if not net:
            debug("Could not load netlist file")
            return

        components = net.getInterestingComponents()

        self.componentGroups = net.groupComponents(components)

        self.kicadSource = net.getSource()
        self.kicadVersion = net.getVersion()
        self.kicadDate = net.getDate()
        self.kiacdTool = net.getTool()

        debug("Loaded",len(components),"components in",len(self.componentGroups),"component groups")

    def getTableData(self,row,col):

        if row < 0 or row >= self.table.rowCount(): return ""
        if col < 0 or col >= self.table.columnCount(): return ""
        item = self.table.item(row,col)

        if not item: return ""
        return str(item.text())

    def extractRowDataFromTable(self, row):

        if row >= self.table.rowCount(): return {}
        #return table row data as a dict
        return dict(zip(self.headings,[self.getTableData(row,i) for i in range(len(self.headings))]))

    def getGroupAtRow(self, row):

        row_data = self.extractRowDataFromTable(row)

        for group in self.componentGroups:

            if group.compareCSVLine(row_data):
                return group

        return None

    def cellDataChanged(self,row,col):

        if self.reloading: return

        group = self.getGroupAtRow(row)

        if not group:
            debug("Group not found @",row,col)
        else:
            #update the CSV data for the group
            item = self.table.item(row,col)
            if not item: return

            group.csvFields[self.headings[col]] = item.text()

    def closeEvent(self, *args, **kwargs):
        event = args[0]

        event.ignore()

        ###do stuff here

        print("Done")

        event.accept()

def main():
    
    app = QApplication(sys.argv)
    ex = BOMWidget(sys.argv)
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()
    
