
import xml.etree.ElementTree as ET

test = {}
cont = 0

def run(messageIsRequest, message):
   global cont
   print cont
   cont += 1
   print "hello"
   return message

