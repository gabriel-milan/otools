__all__ = ['Service']

from otools.status.StatusCode import StatusCode
from copy import deepcopy

class Service ():
  """
  A Service is a class that shall encapsulate your own class in order to 
  attach it into a context. It has four core methods: "setup", 
  "main", "loop" and "finalize". The "setup" method will run once.
  The "main" method will run once every execution loop on the main
  thread. The "loop" method will loop forever, unless the service is
  diabled. The "finalize" method will run when the program shuts down.
  """

  def __init__ (self, obj, context = None):
    try:
      self.__name = obj.name
    except:
        self.__name = obj.__name__
    self.__context = context
    self.__rawObj = deepcopy(obj)
    self.__obj = obj
    self.__obj.__init__(self.__obj)
    self.__obj.MSG_VERBOSE  = self.MSG_VERBOSE
    self.__obj.MSG_DEBUG    = self.MSG_DEBUG
    self.__obj.MSG_INFO     = self.MSG_INFO
    self.__obj.MSG_WARNING  = self.MSG_WARNING
    self.__obj.MSG_ERROR    = self.MSG_ERROR
    self.__obj.MSG_FATAL    = self.MSG_FATAL
    self._active = True
  
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
    return "<OTools Service (name={})>".format(self.name)

  def __repr__ (self):
    return self.__str__()
  
  def setup (self):
    try:
      self.__obj.setup(self.__obj)
      return StatusCode.SUCCESS
    except AttributeError:
      return StatusCode.SUCCESS
    except:
      return StatusCode.FAILURE

  def main (self):
    if self.active:
      try:
        self.__obj.main(self.__obj)
        return StatusCode.SUCCESS
      except AttributeError:
        return StatusCode.SUCCESS
      except:
        return StatusCode.FAILURE

  def loop (self):
    while self.active:
      try:
        self.getContext().getWatchdog().startTimer(self.name, 'loop', self.getContext().name)
        self.__obj.loop(self.__obj)
        self.getContext().getWatchdog().resetTimer(self.name, 'loop', self.getContext().name)
      except AttributeError:
        break
      except:
        pass

  def finalize (self):
    try:
      self.__obj.finalize(self.__obj)
      self.deactivate()
      return StatusCode.SUCCESS
    except AttributeError:
      return StatusCode.SUCCESS
    except:
      return StatusCode.FAILURE

  def setContext (self, ctx):
    self.__context = ctx
    self.__obj.terminateContext   = self.__context.finalize
    self.__obj.getService         = self.__context.getService
    self.__obj.getDataframe       = self.__context.getDataframe
  
  def getContext (self):
    return self.__context

  def deactivate (self):
    self._active = False

  def reset (self):
    self.__init__(self.__rawObj, self.getContext())
    self.setContext(self.getContext())

  @property
  def name(self):
    return self.__name

  @property
  def active(self):
    return self._active