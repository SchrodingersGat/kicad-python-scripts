from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QApplication
import sys
import os

print(sys.argv)

from bomfunk_csv import CSV_DEFAULT as CSV_DEFAULT
from bomfunk_csv import CSV_PROTECTED as CSV_PROTECTED
from bomfunk_csv import CSV_MATCH as CSV_MATCH

import bomfunk_csv

import bomfunk_netlist_reader

ui_path = os.path.join(os.path.dirname(sys.argv[0]),"bomfunk.ui")

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

def colorError():
    return QtGui.QColor(0xCC,0x00,0x00)

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
            if self.csvFile == "" and arg.endswith(".csv") and os.path.isfile(arg):
                self.csvFile = arg

        if self.xmlFile == "" and not self.csvFile == "":
            self.xmlFile = self.csvFile.replace(".csv",".xml")
            
        if not self.xmlFile == "":

            if self.csvFile == "":
                self.csvFile = self.xmlFile.replace(".xml",".csv")
            
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
        self.action_saveCSV.triggered.connect(self.saveCSV)

        self.table.cellChanged.connect(self.cellDataChanged)

        #close events
        self

    def updateHeadings(self):
        self.table.setColumnCount(len(self.headings))
        self.table.setHorizontalHeaderLabels(self.headings)
        
    def loadCSV(self):

        fname = QFileDialog.getOpenFileName(
            None,
            "Load .csv BoM File",
            os.getcwd(),
            "CSV Files (*.csv)")

        self.loadCSVFile(self,fname[0])

    def loadCSVFile(self, fname):

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

        fname = QFileDialog.getOpenFileName(
            None,
            "Load .xml KiCAD Netlist File",
            os.getcwd(),
            "XML Files (*.xml)")

        self.loadXMLFile(str(fname[0]))

    def loadXMLFile(self, fname):

        #blank file
        if not fname or str(fname) == "": return

        print("Loading:",fname)

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

            fname = fname[0]

            if fname.endswith(".csv"):
                self.csvFile = fname
            else:
                return False

        return bomfunk_csv.saveRows(self.csvFile, self.componentGroups, self.kicadSource, self.kicadVersion, self.kicadDate)

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

                kicadData = group.getField(heading)
                csvData = group.getCSVField(heading)

                data = "" #actual data to be displayed

                if heading in CSV_PROTECTED:
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                    if kicadData == "":
                        item.setBackground(colorError())
                    else:
                        item.setBackground(colorProtected())
                    data = kicadData
                else:
                    
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
                    item.setBackground(colorNormal())

                    if kicadData == "" and csvData == "": #no data exists
                        pass
                    elif kicadData == "": #no KiCAD data
                        data = csvData
                        item.setBackground(colorCSV())
                    elif csvData == "": #no CSV data
                        data = kicadData
                        item.setBackground(colorKiCAD())
                    elif csvData == kicadData: #data matches!
                        data = kicadData
                    else: #conflict! (use KiCAD data in preference)
                        data = kicadData
                        item.setBackground(colorConflict())

                item.setText(data)

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
            print("Group not found @",row,col)
        else:
            print("Group @",row,col,">")
            print(group.getRow(CSV_MATCH))

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
    
