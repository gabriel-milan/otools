__all__ = ['OTools']

from otools.core.Context import Context
from otools.logging.Logger import Logger
from otools.logging.LoggingLevel import LoggingLevel
import threading

class OTools ():
  
  def __init__ (self, name = "OTools"):
    self.__name = name
    self.__contexts = {}
    self._logger = Logger(LoggingLevel.INFO).getModuleLogger()
    self.__threads = []

  def __str__ (self):
    return "<OTools Core (name={})>".format(self.name)

  def __repr__ (self):
    return self.__str__()

  def __add__ (self, obj):
    if issubclass (type(obj), Context):
      try:
        if obj.name not in self.__contexts:
          self.__contexts[obj.name] = obj
        else:
          self.warning ("Context with name {} already exists, skipping...".format(obj.name), self.name)
      except:
        self.error ("Failed to get Context name!", self.name)
    else:
      self.fatal ("Only Context objects must be appended here.", self.name)
    return self

  @property
  def name (self):
    return self.__name

  def verbose (self, message, *args, **kws):
    return self._logger.verbose(message, *args, **kws)

  def debug (self, message, *args, **kws):
    return self._logger.debug(message, *args, **kws)

  def info (self, message, *args, **kws):
    return self._logger.info(message, *args, **kws)

  def warning (self, message, *args, **kws):
    return self._logger.warning(message, *args, **kws)

  def error (self, message, *args, **kws):
    return self._logger.error(message, *args, **kws)

  def fatal (self, message, *args, **kws):
    return self._logger.fatal(message, *args, **kws)

  def initialize (self):
    for ctx in self.__contexts:
      self.__contexts[ctx].initialize()

  def execute (self):
    while len(list(self.__contexts)) > 0:
      for ctx in list(self.__contexts):
        if self.__contexts[ctx].active:
          if not self.__contexts[ctx].running:    
            new_thread = threading.Thread(target=self.__contexts[ctx].execute, args=())
            new_thread.name = ctx
            new_thread.daemon = True
            new_thread.start()
            self.__threads.append(new_thread)
            self.__contexts[ctx].running = True
        else:
          del self.__contexts[ctx]
      for t in self.__threads:
        if not t.isAlive():
          if t.name in self.__contexts:
            self.__contexts[t.name].running = False
          t.name = ""
      self.__threads = [t for t in self.__threads if t.name != ""]

  def finalize (self):
    for ctx in self.__contexts:
      self.__contexts[ctx].finalize()