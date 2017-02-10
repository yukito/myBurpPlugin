# -*- coding: utf-8 -*-

from burp import IBurpExtender
from burp import IProxyListener
from burp import IHttpRequestResponse

from java.util import List, ArrayList

import os

class BurpExtender(IBurpExtender, IProxyListener):
   def registerExtenderCallbacks(self, callbacks):
      self._callbacks = callbacks
      self._helpers = callbacks.getHelpers()

      callbacks.registerProxyListener(self)

      return

   def processProxyMessage(self, messageIsRequest, message):
      if messageIsRequest:
         print self._helpers.bytesToString(message.getMessageInfo().getRequest())

