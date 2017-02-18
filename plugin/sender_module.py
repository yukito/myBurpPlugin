# -*- coding: utf-8 -*-

from burp import IBurpExtender
from burp import ITab
from burp import IProxyListener
from burp import IHttpRequestResponse

from java.util import List, ArrayList

from javax.swing import (JPanel, JTable, JButton, JTextField, JLabel, JScrollPane, JMenuItem, JCheckBox, JFileChooser)
from javax.swing.table import DefaultTableModel
from java.awt import (GridBagLayout, GridBagConstraints)
from java.awt.event import ActionListener
import java

import sys, os, imp

module_path = "your path"

class moduleImporter(object):
   def __init__(self):
      self.module_code = ""

   def find_module(self, fullname, path=None):
      fullpath = module_path + fullname if fullname[-3:] == ".py" else module_path + fullname + ".py"
      if os.path.exists(fullpath):
         with open(fullpath, "r") as fp:
            self.module_code = fp.read()
         return self
      else:
         return None

   def load_module(self, name):
      module = imp.new_module(name)
      exec self.module_code in module.__dict__
      sys.modules[name] = module
      return module

class MyTableModel(DefaultTableModel):
   def getColumnClass(self, columnIndex):
      if columnIndex == 0:
          return java.lang.Boolean.TYPE.getClass(self.getValueAt(0, columnIndex))
      return DefaultTableModel.getColumnClass(self, columnIndex)

class BurpExtender(IBurpExtender, ITab, IProxyListener):

   def exec_module(self, messageIsRequest = 0, message = None):
      sys.meta_path = [moduleImporter()]
      modules = [m[1] for m in self.dataModel.getDataVector() if m[0]]
      print modules
#      modules = os.listdir(module_path)
      for module in modules:
         module_name = module[:-3] if module[-3:] == ".py" else module
         exec("import " + module_name)
         sys.modules[module_name].run(messageIsRequest, message)

   def registerExtenderCallbacks(self, callbacks):
      self._callbacks = callbacks
      self._helpers = callbacks.getHelpers()
      callbacks.setExtensionName("Module Importer")
      self.out = callbacks.getStdout()


      self.tab = JPanel(GridBagLayout())
      self.tableData = [
      ]
      colNames = ('Enabled','Module')
      self.dataModel = MyTableModel(self.tableData, colNames)
      self.table = JTable(self.dataModel)
      self.tablecont = JScrollPane(self.table)
      c = GridBagConstraints()
      c.anchor = GridBagConstraints.FIRST_LINE_START
      c.gridx = 0 
      c.gridy = 1 
      c.gridheight = 6 
      c.gridwidth = 6
      c.weightx = 0.3 
      c.weighty = 0.5 
      self.tab.add(self.tablecont, c)

      self.fc = JFileChooser()
      self.fc.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY)

      c = GridBagConstraints()
      c.gridx = 1 
      c.gridy = 0 
      self.openButton = JButton("Open Directory", actionPerformed = self.openDialog)
      self.tab.add(self.openButton, c)

      c = GridBagConstraints()
      c.gridx = 0 
      c.gridy = 0 
      self.input_id = JTextField(40)
      self.tab.add(self.input_id, c)

      callbacks.customizeUiComponent(self.tab)
      callbacks.customizeUiComponent(self.table)
      callbacks.customizeUiComponent(self.tablecont)
      callbacks.addSuiteTab(self)


      callbacks.registerProxyListener(self)

      return

   def getTabCaption(self):
      return("ModuleImporter")

   def getUiComponent(self):
      return self.tab

   def openDialog(self, e):
      returnVal = self.fc.showOpenDialog(None)
      if returnVal == JFileChooser.APPROVE_OPTION:
         self.dataModel.setRowCount(0)
         self.input_id.text = str(self.fc.getSelectedFile())
         modules = os.listdir(self.input_id.text)
         for module in modules:
            if module.split('.')[-1] == "py":
               table_list = [java.lang.Boolean.TRUE, module]
               self.dataModel.insertRow(0, table_list)
      else:
         print("Open command cancelled by user.\n")

   def processProxyMessage(self, messageIsRequest, message):
      self.exec_module(messageIsRequest, message)

