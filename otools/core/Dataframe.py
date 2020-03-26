__all__ = ['Dataframe']

from otools.status.StatusCode import StatusCode
from threading import Lock
from collections import OrderedDict

class Dataframe ():
  """
  A Dataframe is an object to which you can set multiple values and access
  from Context objects on which they're attached
  """

  def __init__ (self, name = "Dataframe"):
    self.__name = name
    self.__context = None
    self.__dict = OrderedDict()
    self.__rlock = Lock()
    self.__wlock = Lock()

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

  def __str__ (self):
    return "<OTools Dataframe (name={})>".format(self.name)

  def __repr__ (self):
    return self.__str__()

  @property
  def name (self):
    return self.__name

  def setup (self):
    return StatusCode.SUCCESS

  def main (self):
    return StatusCode.SUCCESS

  def finalize (self):
    del self.__dict
    return StatusCode.SUCCESS

  def setContext (self, ctx):
    self.__context = ctx
  
  def getContext (self):
    return self.__context

  def get (self, key, blockReading=False, blockWriting=True, timeout=-1):
    if blockReading:
      self.__rlock.acquire(timeout = timeout)
    if blockWriting:
      self.__wlock.acquire(timeout = timeout)
    if key in self.__dict:
      value = self.__dict[key]
    else:
      value = None
      message = "Key {} not found on Dataframe {}.".format(key, self.name)
      self.MSG_ERROR(message)
    if blockReading:
      self.__rlock.release()
    if blockWriting:
      self.__wlock.release()
    return value

  def set (self, key, value, blockReading=True, blockWriting=True, timeout=-1):
    if blockReading:
      self.__rlock.acquire(timeout = timeout)
    if blockWriting:
      self.__wlock.acquire(timeout = timeout)

    self.__dict[key] = value

    if blockReading:
      self.__rlock.release()
    if blockWriting:
      self.__wlock.release()
