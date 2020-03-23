__all__ = ['Logger']

import logging
from otools.exceptions.FatalError import FatalError
from otools.logging.LoggingLevel import LoggingLevel

logging.addLevelName(LoggingLevel.VERBOSE, "VERBOSE")
logging.addLevelName(LoggingLevel.FATAL,    "FATAL" )

module = "Unknown"
context = "Unknown"

def _getAnyException(args):
  """
  Checks if any exception must be raised
  """
  exceptionType = [issubclass(arg,BaseException) if type(arg) is type else False for arg in args]
  Exc = None
  if any(exceptionType):
    args = list(args)
    Exc = args.pop( exceptionType.index( True ) )
    args = tuple(args)
  return Exc, args

def verbose(self, message, moduleName="Unknown", contextName="Unknown", *args, **kws):
  """
    Attempt to emit verbose message
  """
  global module
  module = moduleName
  global context
  context = contextName
  if self.isEnabledFor(LoggingLevel.VERBOSE):
    self._log(LoggingLevel.VERBOSE, message, args, **kws) 

def debug(self, message, moduleName="Unknown", contextName="Unknown", *args, **kws):
  """
    Attempt to emit debug message
  """
  global module
  module = moduleName
  global context
  context = contextName
  if self.isEnabledFor(LoggingLevel.DEBUG):
    self._log(LoggingLevel.DEBUG, message, args, **kws)

def info(self, message, moduleName="Unknown", contextName="Unknown", *args, **kws):
  """
    Attempt to emit info message
  """
  global module
  module = moduleName
  global context
  context = contextName
  if self.isEnabledFor(LoggingLevel.INFO):
    self._log(LoggingLevel.INFO, message, args, **kws) 

def warning(self, message, moduleName="Unknown", contextName="Unknown", *args, **kws):
  """
    Attempt to emit warning message
  """
  global module
  module = moduleName
  global context
  context = contextName
  Exc, args = _getAnyException(args)
  if self.isEnabledFor(LoggingLevel.WARNING):
    self._log(LoggingLevel.WARNING, message, args, **kws) 
  if Exc is not None:
    if args:
      raise Exc(message % (args if len(args) > 1 else args[0]))
    else:
      raise Exc(message)

def error(self, message, moduleName="Unknown", contextName="Unknown", *args, **kws):
  """
    Attempt to emit error message
  """
  global module
  module = moduleName
  global context
  context = contextName
  Exc, args = _getAnyException(args)
  if self.isEnabledFor(LoggingLevel.ERROR):
    self._log(LoggingLevel.ERROR, message, args, **kws) 
  if Exc is not None:
    if args:
      raise Exc(message % (args if len(args) > 1 else args[0]))
    else:
      raise Exc(message)

def fatal(self, message, moduleName="Unknown", contextName="Unknown", *args, **kws):
  """
    Attempt to emit fatal message
  """
  global module
  module = moduleName
  global context
  context = contextName
  Exc, args = _getAnyException(args)
  if Exc is None: Exc = FatalError
  if self.isEnabledFor(LoggingLevel.FATAL):
    self._log(LoggingLevel.FATAL, message, args, **kws) 
  if args:
    raise Exc(message % (args if len(args) > 1 else args[0]))
  else:
    raise Exc(message)

logging.Logger.verbose = verbose
logging.Logger.debug = debug
logging.Logger.info = info
logging.Logger.warning = warning
logging.Logger.error = error
logging.Logger.fatal = fatal

class ContextFilter(logging.Filter):
  def filter(self, record):
    global module
    global context
    record.module = module
    record.context = context
    return True

class Logger ():
  """
  Main class for logging
  """

  def _getFormatter(self):

    class Formatter(logging.Formatter):

      black = '0;30'
      red = '0;31'
      green = '0;32'
      yellow = '0;33'
      blue = '0;34'
      magenta = '0;35'
      cyan = '0;36'
      white = '0;37'
      
      bold_black = '1;30'
      bold_red = '1;31'
      bold_green = '1;32'
      bold_yellow = '1;33'
      bold_blue = '1;34'
      bold_magenta = '1;35'
      bold_cyan = '1;36'
      bold_white = '1;37'

      reset_seq = "\033[0m"
      color_seq = "\033[%(color)sm"
      colors = {
                 'VERBOSE':  white,
                 'DEBUG':    cyan,
                 'INFO':     green,
                 'WARNING':  bold_yellow,
                 'ERROR':    red,
                 'FATAL':    bold_red,
               }
    
      def __init__(self, msg):
        logging.Formatter.__init__(self, self.color_seq + msg + self.reset_seq )
  
      def format(self, record):
        if not(hasattr(record,'nl')):
          record.nl = True
        levelname = record.levelname
        if not 'color' in record.__dict__ and levelname in self.colors:
          record.color = self.colors[levelname]
        return logging.Formatter.format(self, record)
  
    formatter = Formatter("%(asctime)s | OTools >> %(context)s >> %(module)-33.33s %(levelname)7.7s %(message)s")
    return formatter

  def __init__(self, level = LoggingLevel.INFO):
    self.__level = level
    self.__logger = logging.getLogger(self.__class__.__name__)
    self.__ch = logging.StreamHandler()
    self.__ch.setLevel(self.__level)
    self.__ch.setFormatter(self._getFormatter())
    self.__logger.handlers = []
    self.__logger.addHandler(self.__ch)
    self.__logger.addFilter(ContextFilter())
    self.__logger.setLevel(self.__level)

  def setLevel(self, lvl):
    self.__level = lvl
    self.__logger.setLevel(self.__level)
    self.__ch.setLevel(lvl)

  def getLevel(self):
    return self.__level

  def getModuleLogger(self):
    return self.__logger
  
  def __str__ (self):
    return "<OTools Logger (level={})>".format(self.__level)

  def __repr__ (self):
    return self.__str__()