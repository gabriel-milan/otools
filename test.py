from otools import Logger, LoggingLevel, FatalError, OTools, Tool, Context
from time import sleep

a = Logger(LoggingLevel.VERBOSE).getModuleLogger()
a.verbose ("Verbose message")
a.debug ("Debug message")
a.info ("Info message")
a.warning ("Warning message")
a.error ("Error message")
try:
  a.fatal ("Fatal message (error handling prevents this from crashing)")
except FatalError:
  pass

class MyTool ():

  def __init__ (self):
    self._i = 0

  def initialize (self):
    self.MSG_INFO ("Initialize done")
  
  def execute (self):
    self._i += 1
    self.MSG_VERBOSE ("Verbose")
    self.MSG_DEBUG ("Debug")
    self.MSG_INFO ("Info")
    self.MSG_WARNING ("Warning")
    self.MSG_ERROR ("Error")
    if (self._i > 3):
      self.terminateContext()

  def finalize (self):
    self.MSG_INFO ("Finalize done")

class MyTool2 ():

  def __init__ (self):
    self._i = 0

  def initialize (self):
    self.MSG_INFO ("Initialize done")
  
  def execute (self):
    sleep(1)
    self._i += 1
    self.MSG_VERBOSE ("Verbose")
    self.MSG_DEBUG ("Debug")
    self.MSG_INFO ("Info")
    self.MSG_WARNING ("Warning")
    self.MSG_ERROR ("Error")
    if (self._i > 5):
      self.terminateContext()

  def finalize (self):
    self.MSG_INFO ("Finalize done")

ctx = Context(level = LoggingLevel.VERBOSE)
ctx += Tool(MyTool)

ctx2 = Context(name = "Context2")
ctx2 += Tool(MyTool2)

main = OTools()
main += ctx
main += ctx2

main.initialize()
main.execute()
main.finalize()