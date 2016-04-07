import sys

import wx

import wx.grid

from KIBOM_debug import Debug

import KIBOM_columns

import bomfunk_netlist_reader

class BOMTable(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self,parent)
        
        #Setup default columns
        self.SetupColumns(KIBOM_columns.BOM_HEADERS_DEFAULT)
        
    #configure column headings
    def SetupColumns(self, columns):
        
        self.CreateGrid(0, len(columns))
        
        for i,h in enumerate(columns):
            self.SetColLabelValue(i,h)

class BomFrame(wx.Frame):
    
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent,title=title)
        
        self.panel = wx.Panel(self)
        
        self.table = BOMTable(self.panel)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.table, 1, wx.EXPAND)
        
        self.panel.SetSizer(self.sizer)
        
        self.AddMenuBar()
        
        self.Show(True)        
        
    def AddMenuBar(self):
        #add a menu
        filemenu = wx.Menu()
        
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit"," Exit the BoM Manager")
        
        menuBar = wx.MenuBar()
        
        menuBar.Append(filemenu,"&File")
        self.SetMenuBar(menuBar)
        
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        
    def OnExit(self, e):
        self.Close(True)
        
Debug("starting")

app = wx.App(False)

frame = BomFrame(None,"KiBoM")

app.MainLoop()