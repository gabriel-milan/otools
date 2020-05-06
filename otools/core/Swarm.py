__all__ = [
    'Swarm'
]

from otools.status.StatusCode import StatusCode
from otools.core.Service import Service
from functools import wraps
from copy import deepcopy

class Swarm ():
  """
  A Swarm helps deploying multiple similar Service objects
  by handling everything the user should do in order to deploy
  them with much fewer lines of code.
  """

  def __init__ (self, size=1, obj=None, context=None):

    self.__context = context
    self.__services = []
    self.__name = "Otools Swarm <None>"
    self.__objName = None
    self.__size = size
    if obj:
      self.__call__(obj)
    self._active = True

  def __call__ (self, obj, context=None, index=None):

    @wraps(obj)
    def init(obj, index=0):
      self.__objName = obj.__name__
      new_obj = deepcopy(obj)
      self.__rawObj = deepcopy(new_obj)
      new_obj.name = "{}_{}".format(self.__objName, index)
      svc = Service(new_obj)
      self.__services.append(svc)

    for i in range(self.size):
      init(obj, i)

    return self
  
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
    return "<OTools Swarm (obj={}, size={})>".format(self.name, self.size)

  def __repr__ (self):
    return self.__str__()
  
  def setup (self):
    return StatusCode.SUCCESS

  def main (self):
    return StatusCode.SUCCESS

  def loop (self):
    return StatusCode.SUCCESS

  def finalize (self):
    return StatusCode.SUCCESS

  def setContext (self, ctx):
    self.__context = ctx
    for service in self.__services:
      self.__context += service

  def getContext (self):
    return self.__context

  def deactivate (self):
    self._active = False

  def reset (self):
    for service in self.__services:
      service.reset()

  @property
  def name(self):
    return self.__name

  @property
  def active(self):
    return self._active

  @property
  def size(self):
    return self.__size

  @property
  def modules(self):
    return self.__services