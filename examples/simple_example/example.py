#
# Setting up the Context
#
from otools import Context, LoggingLevel
context = Context(level = LoggingLevel.INFO, name = "MyContext")

#
# Setting up the Dataframe
#
from otools import Dataframe
dataframe = Dataframe(name = "MyDataframe")
context += dataframe

#
# Setting up two Services
#
from otools import Service
from time import sleep

@context.add
@Service
class MyCode ():
   # All methods here are optional
   def setup (self):
      # Do whatever you need here
      pass
   def main (self):
      # I'll just print something
      self.MSG_INFO("Hey, I'm being executed!")
      sleep(2)
   def loop (self):
      # I'll print here using WARNING level
      self.MSG_WARNING("A warning log here!")
      sleep(1)
   def finalize (self):
      # Stop!
      self.MSG_INFO("Shutting down...")
      pass

@context.add
@Service
class MySecondCode ():
   def setup(self):
      self.loopCounter = 0
   def main(self):
      self.loopCounter += 1
      if self.loopCounter >= 5:
         self.MSG_INFO("I'm shutting everything down!")
         self.terminateContext()

#
# Setting up the OTools object
#
from otools import OTools

main = OTools()
main += context
main.setup()

#
# Run!
#
main.run()