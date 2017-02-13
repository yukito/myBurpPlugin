# -*- coding: utf-8 -*-

from burp import IBurpExtender
from burp import IProxyListener
from burp import IHttpRequestResponse

from java.util import List, ArrayList

import json
import sys
import os
import imp

module_path = "your module path"

class moduleImporter(object):
   def __init__(self):
      self.module_code = ""

   def find_module(self, fullname, path=None):
      dist_files = os.listdir(module_path)
      if fullname in dist_files or fullname + ".py" in dist_files:
         with open(module_path + fullname + ".py") as fp:
            self.module_code = fp.read()
         return self
      else:
         return None

   def load_module(self, name):
      module = imp.new_module(name)
      exec self.module_code in module.__dict__
      sys.modules[name] = module
      return module


class BurpExtender(IBurpExtender, IProxyListener):

   def exec_module(self, messageIsRequest = 0, message = None):
      sys.meta_path = [moduleImporter()]
      modules = os.listdir(module_path)
      for module in modules:
         if module[-3:] == ".py":
            module_name = module[:-3]
         else:
            module_name = module
         exec("import " + module_name)
         sys.modules[module_name].run(messageIsRequest, message)

   def registerExtenderCallbacks(self, callbacks):
      self._callbacks = callbacks
      self._helpers = callbacks.getHelpers()

      callbacks.registerProxyListener(self)

      return

   def processProxyMessage(self, messageIsRequest, message):
      self.exec_module(messageIsRequest, message)
      if messageIsRequest:
         print self._helpers.bytesToString(message.getMessageInfo().getRequest())
