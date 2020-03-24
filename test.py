from otools import Logger, LoggingLevel, FatalError, OTools, Service, Context, Dataframe, Trigger, TriggerCondition
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
    df = self.getDataframe("MyDF")
    if df.get('counter') == None:
      df.set('counter', 1)
    else:
      df.set('counter', df.get('counter') + 1)
    self.MSG_INFO ("Shared counter value is {}".format(df.get('counter')))
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
    df = self.getDataframe("MyDF")
    if df.get('counter') == None:
      df.set('counter', 1)
    else:
      df.set('counter', df.get('counter') + 1)
    self.MSG_INFO ("Shared counter value is {}".format(df.get('counter')))
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

class MyCondition ():
  def main (self):
    value = self.getDataframe("MyDF").get('counter')
    if value >= 5:
      self.MSG_WARNING("MyDF counter is {}, I'm triggering now.".format(value))
    return value >= 5

class MyAction ():
  def main (self):
    df = self.getDataframe("MyDF").set('counter', 0)
  def loop (self):
    self.MSG_WARNING("This is ignored!")

sharedDataframe = Dataframe(name = "MyDF")
splitDataframe1 = Dataframe(name = "Split")
splitDataframe2 = Dataframe(name = "Split")
loopDataframe = Dataframe(name = "LoopDF")

trigger = Trigger()
trigger += TriggerCondition(MyCondition)
trigger += Service(MyAction)

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
ctx2 += trigger

main = OTools()
main += ctx
main += ctx2

main.setup()
main.run()
main.finalize()