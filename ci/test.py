from otools import Logger, LoggingLevel, FatalError, OTools, Service, Context, Dataframe, Trigger, TriggerCondition, Swarm
from time import sleep
from random import randint

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

main = OTools()
ctx = Context(level = LoggingLevel.VERBOSE)
ctx2 = Context(name = "Context2")
ctx3 = Context(name = "SwarmContext")
trigger = Trigger()

@ctx.add
@Service
class MyService ():
  def __init__ (self):
    self._i = 0
  def setup (self):
    self.MSG_INFO ("setup done")
  def main (self):
    # Uncommenting the following line triggers the Watchdog
    # sleep(11)
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
    # Uncommenting the following line triggers the Watchdog
    # sleep(11)
    df = self.getDataframe("LoopDF")
    if df.get('counter') == None:
      df.set('counter', 1)
    else:
      df.set('counter', df.get('counter') + 1)
    self.MSG_INFO ("Shared counter value is {}, this increments every 0.5 seconds for both contexts".format(df.get('counter')))
  def finalize (self):
    self.MSG_INFO ("Finalize done")

@main.Watchdog.add
@ctx2.add
@Service
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

@main.Watchdog.add
@ctx3.add
@Swarm(5)
class SwarmTest():
  def setup (self):
    self.i = 1
  def main (self):
    self.MSG_WARNING("Hey, I'm here! ({})".format(self.name))
    self.MSG_INFO("This is i={}".format(self.i))
    sleep(1)
    self.i += 1
    if self.i >= 4:
      self.MSG_WARNING("Will shut this thing down!")
      self.terminateContext()
      self.MSG_WARNING("Did it!")
  def loop (self):
    self.MSG_INFO("Looping... yay!!!")
    sleep (.5)

@trigger.add
@TriggerCondition
class MyCondition ():
  def main (self):
    value = self.getDataframe("MyDF").get('counter')
    if value >= 5:
      self.MSG_WARNING("MyDF counter is {}, I'm triggering now.".format(value))
    return value >= 5

@trigger.add
@Service
class MyAction ():
  def main (self):
    df = self.getDataframe("MyDF").set('counter', 0)
  def loop (self):
    self.MSG_WARNING("This is ignored!")

sharedDataframe = Dataframe(name = "MyDF")
splitDataframe1 = Dataframe(name = "Split")
splitDataframe2 = Dataframe(name = "Split")
loopDataframe = Dataframe(name = "LoopDF")

ctx += sharedDataframe
ctx += splitDataframe1
ctx += loopDataframe

ctx2 += sharedDataframe
ctx2 += splitDataframe2
ctx2 += loopDataframe
ctx2 += trigger

main += ctx
main += ctx2
main += ctx3

main.Watchdog += MyService, {
  "loop": {
    "action" : "terminate"
  }
}
main.Watchdog.printCollection()

main.setup()
main.run()
main.finalize()