# -*- coding: utf-8 -*-

from burp import IBurpExtender
from burp import ITab
from burp import IProxyListener
from burp import IHttpRequestResponse

from java.util import List, ArrayList

from javax.swing import (JPanel, JTable, JButton, JTextField, JLabel, JScrollPane, JMenuItem, JCheckBox, JFileChooser)
from javax.swing.table import DefaultTableModel
from java.awt import (GridBagLayout, GridBagConstraints, Dimension)
from java.awt.event import ActionListener
import java

import sys, os, imp, types

M_PATH = "/Users/yukito/prog/python/myBurpPlugin/plugin/module/" # set your module path which you want to fix like "/home/user/module/"

VALUE_TYPES = [types.IntType, types.LongType, types.FloatType, types.StringType, types.UnicodeType, types.TupleType, types.ListType, types.DictType]

M_VALUABLES = {}

class moduleImporter(object):
   def __init__(self, module_path = "", messageIsRequest = 0, message = None):
      self.module_code = ""
      self.module_path = module_path
      self.messageIsRequest = messageIsRequest
      self.message = message

   def find_module(self, fullname, path=None):
      fullpath = self.module_path + fullname if fullname[-3:] == ".py" else self.module_path + fullname + ".py"
      if os.path.exists(fullpath):
         with open(fullpath, "r") as fp:
            self.module_code = fp.read()
         return self
      else:
         return None

   def load_module(self, name):
      module = imp.new_module(name)
      exec self.module_code in module.__dict__
      self.load_valuable(module, name)
      self.message = module.run(self.messageIsRequest, self.message)
      self.save_valuable(module, name)
      return None

   # This burp plugin can't persistent valuables in module. So valuables in module should be saved in this burp plugin itself.
   def save_valuable(self, module, module_name):
      for i in dir(module):
         exec("typeof_valuable = type(module." + i + ")")
         # decide attribute of module as valuable if type of attribute is in VALUE_TYPES.
         if typeof_valuable in VALUE_TYPES and i[0] != "_":
            exec("M_VALUABLES[module_name][i] = module." + i)

   def load_valuable(self, module, module_name):
      try:
         for valuable in M_VALUABLES[module_name]:
            exec("module." + valuable + " = M_VALUABLES[module_name][valuable]")
      except:
         M_VALUABLES[module_name] = {}

class MyTableModel(DefaultTableModel):
   def getColumnClass(self, columnIndex):
      if columnIndex == 0:
          return java.lang.Boolean.TYPE.getClass(self.getValueAt(0, columnIndex))
      return DefaultTableModel.getColumnClass(self, columnIndex)

class BurpExtender(IBurpExtender, ITab, IProxyListener):

   def exec_module(self, messageIsRequest = 0, message = None):
      module_path = M_PATH if M_PATH else str(self.fc.getSelectedFile()) + "/"
      sys.meta_path = [moduleImporter(module_path, messageIsRequest, message)]
      modules = [m[1] for m in self.dataModel.getDataVector() if m[0]]
      #modules = os.listdir(module_path)
      for module in modules:
         module_name = module[:-3] if module[-3:] == ".py" else module
         exec("import " + module_name)
      return sys.meta_path[0].message

   def registerExtenderCallbacks(self, callbacks):
      self._callbacks = callbacks
      self._helpers = callbacks.getHelpers()
      callbacks.setExtensionName("Module Importer")
      self.out = callbacks.getStdout()

      self.tab = JPanel(GridBagLayout())
      self.tableData = []
      colNames = ('Enabled','Module')
      self.dataModel = MyTableModel(self.tableData, colNames)
      self.table = JTable(self.dataModel)
      self.tablecont = JScrollPane(self.table)
      c = GridBagConstraints()
      c.anchor = GridBagConstraints.FIRST_LINE_START
      c.gridx = 0 
      c.gridy = 4 
      c.gridheight = 6 
      c.gridwidth = 6
      c.weightx = 0.6 
      c.weighty = 0.5 
      self.tab.add(self.tablecont, c)

      self.fc = JFileChooser()
      self.fc.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY)

      label_for_openDirectory = JLabel("Module Importer")
      c = GridBagConstraints()
      c.anchor = GridBagConstraints.FIRST_LINE_START
      c.gridx = 0 
      c.gridy = 0 
      self.tab.add(label_for_openDirectory, c)

      label_plugin_desc = JLabel("This module makes your development of Burp Suite Plugin easier.")
      label_plugin_desc.setPreferredSize(Dimension(400, 50))
      c = GridBagConstraints()
      c.gridx = 0 
      c.gridy = 1 
      self.tab.add(label_plugin_desc, c)

      label_for_openDirectory = JLabel("Module Path:")
      c = GridBagConstraints()
      c.anchor = GridBagConstraints.FIRST_LINE_START
      c.gridx = 0 
      c.gridy = 2 
      self.tab.add(label_for_openDirectory, c)

      c = GridBagConstraints()
      c.anchor = GridBagConstraints.FIRST_LINE_START
      c.gridx = 0 
      c.gridy = 3 
      self.input_id = JTextField(40)
      self.input_id.setEditable(java.lang.Boolean.FALSE)
      self.tab.add(self.input_id, c)

      c = GridBagConstraints()
      c.anchor = GridBagConstraints.FIRST_LINE_START
      c.gridx = 1 
      c.gridy = 3 
      self.openButton = JButton("Open Directory", actionPerformed = self.openDialog)
      self.tab.add(self.openButton, c)

      if M_PATH:
         self.set_fixed_module_path()

      #callbacks.customizeUiComponent(self.tab)
      #callbacks.customizeUiComponent(self.table)
      #callbacks.customizeUiComponent(self.tablecont)
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
            M_VALUABLES[module[:-3]] = {}
            if module.split('.')[-1] == "py":
               table_list = [java.lang.Boolean.TRUE, module]
               self.dataModel.insertRow(0, table_list)
      else:
         print("Open command cancelled by user.\n")

   def set_fixed_module_path(self):
      self.input_id.text = M_PATH
      modules = os.listdir(self.input_id.text)
      for module in modules:
         M_VALUABLES[module[:-3]] = {}
         if module.split('.')[-1] == "py":
            table_list = [java.lang.Boolean.TRUE, module]
            self.dataModel.insertRow(0, table_list)

   def processProxyMessage(self, messageIsRequest, message):
      if messageIsRequest:
         request = message.getMessageInfo().getRequest()
         readabled = self._helpers.bytesToString(request)
         modified_string_message = self.exec_module(messageIsRequest, readabled)
         modified_byte_message = self._helpers.stringToBytes(modified_string_message)
         message.getMessageInfo().setRequest(modified_byte_message)
      else:
         response = message.getMessageInfo().getResponse()
         readabled = self._helpers.bytesToString(response)
         modified_string_message = self.exec_module(messageIsRequest, readabled)
         modified_byte_message = self._helpers.stringToBytes(modified_string_message)
         message.getMessageInfo().setResponse(modified_byte_message)
