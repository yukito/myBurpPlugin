# -*- coding: utf-8 -*-

from burp import IBurpExtender
from burp import IProxyListener
from burp import IHttpRequestResponse

from java.util import List, ArrayList

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


class BurpExtender(IBurpExtender, IProxyListener):

   def exec_module(self, messageIsRequest = 0, message = None):
      sys.meta_path = [moduleImporter()]
      modules = os.listdir(module_path)
      for module in modules:
         module_name = module[:-3] if module[-3:] == ".py" else module
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
