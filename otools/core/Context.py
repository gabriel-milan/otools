__all__ = ['Context']

from otools.logging.Logger import Logger
from otools.logging.LoggingLevel import LoggingLevel
from otools.core.Service import Service
from otools.core.Dataframe import Dataframe
from otools.status.StatusCode import StatusCode
import threading

class Context ():
  """
  Context is an object that allows communication between modules attached to OTools.
  Your code can have one or more Context objects, allowing you to orchestrate multiple online systems.
  """

  def __init__ (self, level = LoggingLevel.INFO, name = "Unnamed"):

    self._name = name
    self._logger = Logger(level).getModuleLogger()
    self.info("Context with name {} created successfully!".format(self.name))
    self._services = {}
    self._services = {}
    self._dataframes = {}
    self._active = True
    self.running = False
  
  def __str__ (self):
    return "<OTools Context (name={})>".format(self._name)

  def __repr__ (self):
    return self.__str__()

  def __add__ (self, obj):
    if issubclass(type(obj), Service):
      if obj.name in self._services:
        message = "Service with name {} already attached, skipping...".format(obj.name)
        self.warning(message, self.__str__())
        return self
      self.info (" * Adding Service with name {}...".format(obj.name))
      obj.setContext(self)
      self._services[obj.name] = obj
    elif issubclass(type(obj), Dataframe):
      if obj.name in self._dataframes:
        message = "Dataframe with name {} already attached, skipping...".format(obj.name)
        self.warning(message, self.__str__())
        return self
      self.info (" * Adding Dataframe with name {}...".format(obj.name))
      obj.setContext(self)
      self._dataframes[obj.name] = obj
    return self

  def getService (self, serviceName):
    if serviceName in self._services:
      return self._services[serviceName]
    else:
      message = "Service with name {} is not attached into this context!".format(serviceName)
      self.error(message, self.__str__())
      return None

  def getDataframe (self, dataframeName):
    if dataframeName in self._dataframes:
      return self._dataframes[dataframeName]
    else:
      message = "Dataframe with name {} is not attached into this context!".format(dataframeName)
      self.error(message, self.__str__())
      return None

  @property
  def name(self):
    return self._name

  @property
  def active(self):
    return self._active

  def verbose (self, message, moduleName="Unknown", contextName="Unknown", *args, **kws):
    self._logger.verbose(message, moduleName, self.name, *args, **kws)

  def debug (self, message, moduleName="Unknown", contextName="Unknown", *args, **kws):
    self._logger.debug(message, moduleName, self.name, *args, **kws)

  def info (self, message, moduleName="Unknown", contextName="Unknown", *args, **kws):
    self._logger.info(message, moduleName, self.name, *args, **kws)

  def warning (self, message, moduleName="Unknown", contextName="Unknown", *args, **kws):
    self._logger.warning(message, moduleName, self.name, *args, **kws)

  def error (self, message, moduleName="Unknown", contextName="Unknown", *args, **kws):
    self._logger.error(message, moduleName, self.name, *args, **kws)

  def fatal (self, message, moduleName="Unknown", contextName="Unknown", *args, **kws):
    self._logger.fatal(message, moduleName, self.name, *args, **kws)

  def setup (self):
    for service in self._services:
      if self._services[service].setup().isFailure():
        message = "Failed to setup service {}".format(service)
        self.fatal(message, self.__str__())
        return StatusCode.FAILURE
    return StatusCode.SUCCESS

  def main (self):
    for service in self._services:
      if self._services[service].main().isFailure():
        message = "Failed to main service {}".format(service)
        self.fatal(message, self.__str__())
        return StatusCode.FAILURE
    return StatusCode.SUCCESS

  def loop (self):
    for service in list(self._services):
      if self._services[service].active:
        loop_thread = threading.Thread(target=self._services[service].loop, args=())
        loop_thread.name = "{}_loop".format(service)
        loop_thread.daemon = True
        loop_thread.start()

  def finalize (self):
    self._active = False
    for service in self._services:
      if self._services[service].finalize().isFailure():
        message = "Failed to finalize service {}".format(service)
        self.fatal(message, self.__str__())
        return StatusCode.FAILURE
    return StatusCode.SUCCESS
