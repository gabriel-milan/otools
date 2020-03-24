from otools import Logger, LoggingLevel, FatalError, OTools, Service, Context, Dataframe
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

class MyService ():

  def __init__ (self):
    self._i = 0

  def setup (self):
    self.MSG_INFO ("setup done")
  
  def main (self):
    self._i += 1

    # Messaging
    self.MSG_VERBOSE ("Verbose")
    self.MSG_DEBUG ("Debug")
    self.MSG_INFO ("Info")
    self.MSG_WARNING ("Warning")
    self.MSG_ERROR ("Error")

    # Shared dataframe
    df = self.getDataframe("MyDF")
    if df.get('counter') == None:
      df.set('counter', 1)
    else:
      df.set('counter', df.get('counter') + 1)
    self.MSG_INFO ("Shared counter value is {}".format(df.get('counter')))

    # Exclusive dataframe
    split = self.getDataframe("Split")
    if split.get('counter') == None:
      split.set('counter', 1)
    else:
      split.set('counter', split.get('counter') + 1)
    self.MSG_INFO ("Exclusive counter value is {}".format(split.get('counter')))

    if (self._i == 3):
      self.terminateContext()

  def loop (self):
    sleep(0.5)
    df = self.getDataframe("LoopDF")
    if df.get('counter') == None:
      df.set('counter', 1)
    else:
      df.set('counter', df.get('counter') + 1)
    self.MSG_INFO ("Shared counter value is {}, this increments every 0.5 seconds for both contexts".format(df.get('counter')))

  def finalize (self):
    self.MSG_INFO ("Finalize done")

class MyService2 ():

  def __init__ (self):
    self._i = 0

  def setup (self):
    self.MSG_INFO ("setup done")
  
  def main (self):
    sleep(1)
    self._i += 1

    # Messaging
    self.MSG_VERBOSE ("Verbose")
    self.MSG_DEBUG ("Debug")
    self.MSG_INFO ("Info")
    self.MSG_WARNING ("Warning")
    self.MSG_ERROR ("Error")

    # Shared dataframe
    df = self.getDataframe("MyDF")
    if df.get('counter') == None:
      df.set('counter', 1)
    else:
      df.set('counter', df.get('counter') + 1)
    self.MSG_INFO ("Shared counter value is {}".format(df.get('counter')))

    # Exclusive dataframe
    split = self.getDataframe("Split")
    if split.get('counter') == None:
      split.set('counter', 1)
    else:
      split.set('counter', split.get('counter') + 1)
    self.MSG_INFO ("Exclusive counter value is {}".format(split.get('counter')))

    if (self._i == 5):
      self.terminateContext()

  def loop (self):
    sleep(0.5)
    df = self.getDataframe("LoopDF")
    if df.get('counter') == None:
      df.set('counter', 1)
    else:
      df.set('counter', df.get('counter') + 1)
    self.MSG_INFO ("Shared counter value is {}, this increments every 0.5 seconds for both contexts".format(df.get('counter')))

  def finalize (self):
    self.MSG_INFO ("Finalize done")

sharedDataframe = Dataframe(name = "MyDF")
splitDataframe1 = Dataframe(name = "Split")
splitDataframe2 = Dataframe(name = "Split")
loopDataframe = Dataframe(name = "LoopDF")

ctx = Context(level = LoggingLevel.VERBOSE)
ctx += Service(MyService)
ctx += sharedDataframe
ctx += splitDataframe1
ctx += loopDataframe

ctx2 = Context(name = "Context2")
ctx2 += Service(MyService2)
ctx2 += sharedDataframe
ctx2 += splitDataframe2
ctx2 += loopDataframe

main = OTools()
main += ctx
main += ctx2

main.setup()
main.run()
main.finalize()