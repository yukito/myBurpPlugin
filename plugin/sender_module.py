# -*- coding: utf-8 -*-

from burp import IBurpExtender
from burp import IProxyListener
from burp import IHttpRequestResponse

from java.util import List, ArrayList

import json
import sys
import os
import imp

module_path = "/Users/yukito/prog/myBurpPlugin/plugin/module/"

class moduleImporter(object):
   def __init__(self):
      self.module_code = ""

   def find_module(self, fullname, path=None):
      with open(module_path + fullname + ".py") as fp:
         self.module_code = fp.read()
      return self

   def load_module(self, name):
      module = imp.new_module(name)
      exec self.module_code in module.__dict__
      sys.modules[name] = module
      return module


class BurpExtender(IBurpExtender, IProxyListener):
   def registerExtenderCallbacks(self, callbacks):
      self._callbacks = callbacks
      self._helpers = callbacks.getHelpers()

      callbacks.registerProxyListener(self)

      return

   def processProxyMessage(self, messageIsRequest, message):
      sys.meta_path = [moduleImporter()]
      modules = os.listdir(module_path)
      for module in modules:
         exec("import " + module[:-3])
         print sys.modules[module[:-3]].run()
      sys.meta_path = []
      if messageIsRequest:
         print self._helpers.bytesToString(message.getMessageInfo().getRequest())
