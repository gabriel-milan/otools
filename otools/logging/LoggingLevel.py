__all__ = ['LoggingLevel']

import logging

class LoggingLevel ():
  """
  A class for parsing logging level numbers into
  understadable text
  """
  VERBOSE = logging.DEBUG - 1
  DEBUG   = logging.DEBUG
  INFO    = logging.INFO
  WARNING = logging.WARNING
  ERROR   = logging.ERROR
  FATAL   = logging.CRITICAL
  MUTE    = logging.CRITICAL