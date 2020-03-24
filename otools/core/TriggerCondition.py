__all__ = ['TriggerCondition']

from otools.status.StatusCode import StatusTrigger
from otools.core.Service import Service

class TriggerCondition (Service):
  """
  TriggerCondition is a class for encapsulating other classes in order
  to identify it as a condition not as anything else.
  """

  def __init__ (self, obj):
    Service.__init__(self, obj)
    self.__obj = obj

  def main (self):
    if self.active:
      try:
        if (self.__obj.main(self.__obj)):
          return StatusTrigger.TRIGGERED
        else:
          return StatusTrigger.NOT_TRIGGERED
      except:
        self.MSG_WARNING("TriggerCondition with name {} failed to check trigger status".format(self.name))
        return StatusTrigger.NOT_TRIGGERED
  
  def loop (self):
    return

  def __str__ (self):
    return "<OTools TriggerCondition (name={})>".format(self.name)
