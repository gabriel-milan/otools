__all__ = ['Tool']

from otools.status.StatusCode import StatusCode

class Tool ():
  """
  A Tool is a class that shall encapsulate your own class in order to 
  attach it into a context. It has three core methods: "initialize", 
  "execute" and "finalize". The "initialize" method will run once.
  The "execute" method will run once every execution loop on the main
  thread. The "finalize" method will run when the program shuts down.
  """

  def __init__ (self, obj):
    try:
      self.__name = obj.getName()
    except:
      self.__name = obj.__name__
    self.__context = None
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
    return "<OTools Tool (name={})>".format(self.name)

  def __repr__ (self):
    return self.__str__()
  
  def initialize (self):
    try:
      self.__obj.initialize(self.__obj)
      return StatusCode.SUCCESS
    except:
      return StatusCode.FAILURE

  def execute (self):
    if self._active:
      try:
        self.__obj.execute(self.__obj)
        return StatusCode.SUCCESS
      except:
        return StatusCode.FAILURE

  def finalize (self):
    try:
      self.__obj.finalize(self.__obj)
      self._active = False
      return StatusCode.SUCCESS
    except:
      return StatusCode.FAILURE

  def setContext (self, ctx):
    self.__context = ctx
    self.__obj.terminateContext = self.__context.finalize
  
  def getContext (self):
    return self.__context

  @property
  def name(self):
    return self.__name