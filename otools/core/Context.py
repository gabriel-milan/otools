__all__ = ['Context']

from otools.logging.Logger import Logger
from otools.logging.LoggingLevel import LoggingLevel
from otools.core.Tool import Tool
from otools.status.StatusCode import StatusCode

class Context ():
  """
  Context is an object that allows communication between modules attached to OTools.
  Your code can have one or more Context objects, allowing you to orchestrate multiple online systems.
  """

  def __init__ (self, level = LoggingLevel.INFO, name = "Unnamed"):

    self._name = name
    self._logger = Logger(level).getModuleLogger()
    self._tools = {}
    self._services = {}
    self._dataframes = {}
    self._active = True
    self.running = False
  
  def __str__ (self):
    return "<Context (name={})>".format(self._name)

  def __repr__ (self):
    return self.__str__()

  def __add__ (self, obj):
    if issubclass(type(obj), Tool):
      if obj.name in self._tools:
        message = "Tool with name {} already attached, skipping...".format(obj.name)
        self.warning(message, self.__str__())
      obj.setContext(self)
      self._tools[obj.name] = obj
    return self

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

  def initialize (self):
    for tool in self._tools:
      if self._tools[tool].initialize().isFailure():
        message = "Failed to initialize tool {}".format(tool)
        self.fatal(message, self.__str__())
        return StatusCode.FAILURE
    return StatusCode.SUCCESS

  def execute (self):
    for tool in self._tools:
      if self._tools[tool].execute().isFailure():
        message = "Failed to execute tool {}".format(tool)
        self.fatal(message, self.__str__())
        return StatusCode.FAILURE
    return StatusCode.SUCCESS

  def finalize (self):
    self._active = False
    for tool in self._tools:
      if self._tools[tool].finalize().isFailure():
        message = "Failed to finalize tool {}".format(tool)
        self.fatal(message, self.__str__())
        return StatusCode.FAILURE
    return StatusCode.SUCCESS
