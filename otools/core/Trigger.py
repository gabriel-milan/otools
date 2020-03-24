__all__ = ['Trigger']

from otools.core.Service import Service
from otools.core.TriggerCondition import TriggerCondition
from otools.logging.Logger import Logger
from otools.status.StatusCode import StatusCode, StatusTrigger
from collections import OrderedDict

class Trigger ():
  """
  Trigger is a class for implement triggering actions on the
  framework. After being constructed, Service and TriggerCondition
  objects are allowed in order to configure this.

  Few types of triggering are allowed here:
  * and : all conditions must trigger
  * or  : any of the conditions must trigger
  * xor : make a XOR on the conditions, in the order they were attached
  """

  def __init__ (self, name = "Trigger", triggerType = 'or'):

    self.__name = name
    accepted_triggerTypes = ['or', 'and', 'xor']
    if triggerType not in accepted_triggerTypes:
      Logger().getModuleLogger().error("Trigger type {} not allowed! Allowed types are {}".format(triggerType, accepted_triggerTypes), name, "None")
      return StatusCode.FAILURE
    else:
      self.__triggerType = triggerType
    self.__conditions     = OrderedDict()
    self.__executionStack = OrderedDict()
    self.__context = None
    self.__obj = self
    self._active = True

  def __add__ (self, a):

    if issubclass (type(a), TriggerCondition):
      self.__conditions[a.name] = a
    elif issubclass (type(a), Service):
      self.__executionStack[a.name] = a
    else:
      Logger().getModuleLogger().error("Type {} not allowed! You probably should encapsulate it using either Service or TriggerCondition classes".format(type(a)), self.name, self.getContext())
    return self

  def __str__ (self):
    return "<OTools Trigger (name={})>".format(self.name)

  def __repr__ (self):
    return self.__str__()

  @property
  def name(self):
    return self.__name

  @property
  def active(self):
    return self._active

  def MSG_VERBOSE (self, message, moduleName="Unknown", contextName="Unknown", *args, **kws):
    self.__context.verbose(message, self.__name, contextName, *args, **kws)

  def MSG_DEBUG (self, message, moduleName="Unknown", contextName="Unknown", *args, **kws):
    self.__context.debug(message, self.__name, contextName, *args, **kws)

  def MSG_INFO (self, message, moduleName="Unknown", contextName="Unknown", *args, **kws):
    self.__context.info(message, self.__name, contextName, *args, **kws)

  def MSG_WARNING (self, message, moduleName="Unknown", contextName="Unknown", *args, **kws):
    self.__context.warning(message, self.__name, contextName, *args, **kws)

  def MSG_ERROR (self, message, moduleName="Unknown", contextName="Unknown", *args, **kws):
    self.__context.error(message, self.__name, contextName, *args, **kws)

  def MSG_FATAL (self, message, moduleName="Unknown", contextName="Unknown", *args, **kws):
    self.__context.fatal(message, self.__name, contextName, *args, **kws)

  def make_or (self, answers):
    return any(answers)

  def make_and (self, answers):
    return all(answers)

  def make_xor (self, answers):
    from functools import reduce
    return reduce(lambda i, j: i ^ j, answers)

  def setup (self):
    for service in [service for _, service in self.__executionStack.items()]:
      service.setContext(self.getContext())
      if service.setup().isFailure():
        self.MSG_ERROR("Failed to setup Service with name {}".format(service.name))
    for condition in [condition for _, condition in self.__conditions.items()]:
      condition.setContext(self.getContext())
      if condition.setup().isFailure():
        self.MSG_ERROR("Failed to setup TriggerCondition with name {}".format(condition.name))
    return StatusCode.SUCCESS

  def main (self):
    answers = []
    for condition in [condition for _, condition in self.__conditions.items()]:
      answers.append(condition.main())
    if (self.__triggerType == 'or'):
      result = self.make_or(answers)
    elif (self.__triggerType == 'and'):
      result = self.make_and(answers)
    elif (self.__triggerType == 'xor'):
      result = self.make_xor (answers)

    if result == True:
      self.MSG_INFO ("Trigger with name {} triggered! Will now run its stack:".format(self.name))
      for service in [service for _, service in self.__executionStack.items()]:
        self.MSG_INFO (" * Executing Service with name {}".format(service.name))
        if service.main().isFailure():
          self.MSG_ERROR (" * ERROR while executing Service with name {}".format(service.name))
    
    return StatusCode.SUCCESS

  def loop (self):
    return

  def finalize (self):
    for condition in [condition for _, condition in self.__conditions.items()]:
      if condition.finalize().isFailure():
        self.MSG_ERROR("Failed to finalize TriggerCondition with name {}".format(condition.name))

    for service in [service for _, service in self.__executionStack.items()]:
      if service.finalize().isFailure():
        self.MSG_ERROR("Failed to finalize Service with name {}".format(service.name))

    self.deactivate()

    return StatusCode.SUCCESS

  def setContext (self, ctx):
    self.__context = ctx
    self.__obj.terminateContext   = self.__context.finalize
    self.__obj.getService         = self.__context.getService
    self.__obj.getDataframe       = self.__context.getDataframe
  
  def getContext (self):
    return self.__context

  def deactivate (self):
    self._active = False
