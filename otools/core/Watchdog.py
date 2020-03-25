__all__ = ['Watchdog']

from otools.macros import DEFAULT_METHOD_DICT, ACCEPTED_ACTIONS, ACCEPTED_METHODS, WDT_WRITE_ATTEMPTS, WDT_FILENAME, WDT_FILE_OPTIONS, WDT_WRITE_FAIL_REBOOT_TIMEOUT
from otools.core.Service import Service
from otools.logging.Logger import Logger
from otools.logging.LoggingLevel import LoggingLevel
from otools.status.StatusCode import StatusCode
import pprint
from collections import OrderedDict
from copy import deepcopy
from threading import Lock, Thread, Timer
from time import sleep

class Watchdog ():
  """
  The OTools Watchdog is an implementation of a module that
  will take care of eventual infinite loops or methods that
  take too long to run on Service objects. This is an optional
  module of the framework, meaning it can be either enabled or
  disabled as the user wishes.

  The methods that can be monitored are:
   * main: check if one round of the main method takes longer
   than expected;
   * loop: check if one round of the loop method takes longer
   than expected.

  The actions that can be taken when this triggers are:
   * reset: pauses the execution of the context, removes the
   module, re-add it and re-run it;
   * terminate: ends the application. If the Linux watchdog
   option is enabled, this implies in a system reboot;
   * warn: just raises a warning on the logging application.
  """

  def __init__ (self, name = "Watchdog", use_linux_watchdog = False, level = LoggingLevel.INFO):

    self._active = False
    self._enabled = False
    self._useLinuxWatchdog = use_linux_watchdog
    self._modules = OrderedDict()
    self.__name = name
    self.__sendKeepAlive = True
    self.__logger = Logger(level).getModuleLogger()
    self.__contexts = OrderedDict()
    self.__defaultParameters = {
      'main' : deepcopy(DEFAULT_METHOD_DICT),
      'loop'     : deepcopy(DEFAULT_METHOD_DICT),
    }
    self.__acceptedActions = ACCEPTED_ACTIONS
    self.__acceptedMethods = ACCEPTED_METHODS
    self.__resetTimers = True
    self.__lock = Lock()

  def __str__ (self):
    return "<OTools Watchdog (name={})>".format(self.name)

  def __repr__ (self):
    return self.__str__()

  def __add__ (self, module):
    if not ((issubclass(type(module), Service)) or (len(module) == 2)):
      self.error ("Failed to add module to watchdog. Check usage:")
      self.error (" * wd += (module, params_dict)")
      self.error (" * wd += module")
      self.error (" * wd += context")
      return self
    params_dict = deepcopy(self.__defaultParameters)
    custom_params_dict = {}
    try:
      if (len(module) == 2):
        custom_params_dict = module[1]
        module = module[0]
    except:
      pass
    if (issubclass(type(module), Service)):
      self.info (" * Adding Service w/ name {} to the Watchdog...".format(module.name))
    else:
      self.error ("Failed to add module to Watchdog. Supported modules must be encapsulated by the Service class")
      return self
    methods = self.__acceptedMethods
    methods_param = ['enable', 'timeout']
    methods_type = [bool, int]
    for method in methods:
      if (method in custom_params_dict):
        for i in range (len(methods_param)):
          method_param = methods_param [i]
          if (method_param in custom_params_dict[method]):
            if (type(custom_params_dict[method][method_param]) == methods_type[i]):
              params_dict[method][method_param] = custom_params_dict[method][method_param]
            else:
              self.error ("Type \"{}\" not accepted for param \"{}\" on method \"{}\"".format(type(custom_params_dict[method][method_param]), method_param, method))
              return self
        if ('action' in custom_params_dict[method]):
          if (custom_params_dict[method]['action'] in self.__acceptedActions):
            params_dict[method]['action'] = custom_params_dict[method]['action']
          else:
            self.error (self, "Action \"{}\" not accepted on method \"{}\"".format(custom_params_dict[method]['action'], method))
    self.debug ("Acquiring lock for adding new module")
    self.__lock.acquire()
    if (module.getContext().name in self._modules.keys()) and (module.name in self._modules[module.getContext().name].keys()):
      self.error (self, "Failed to add module to Watchdog. Key {} already in WD's dict".format(module.name))
      return self
    if (not module.getContext().name in self._modules.keys()):
      self._modules[module.getContext().name] = {}
    self._modules[module.getContext().name][module.name] = params_dict
    self.info (" * Module {} added to the watchdog successfully!".format(module.name))
    self.debug ("Releasing lock after adding new module")
    self.__lock.release()
    return self

  @property
  def name(self):
    return self.__name

  @property
  def active(self):
    return self._active

  @property
  def enabled(self):
    return self._enabled

  def verbose (self, msg):
    self.__logger.verbose(msg, self.name, "Watchdog")

  def debug (self, msg):
    self.__logger.debug(msg, self.name, "Watchdog")

  def info (self, msg):
    self.__logger.info(msg, self.name, "Watchdog")

  def warning (self, msg):
    self.__logger.warning(msg, self.name, "Watchdog")

  def error (self, msg):
    self.__logger.error(msg, self.name, "Watchdog")

  def fatal (self, msg):
    self.__logger.fatal(msg, self.name, "Watchdog")

  def setup (self):
    if self.enabled:
      self.info ("Enabling Watchdog...")
      loop_thread = Thread(target=self.loop, args=())
      loop_thread.name = "Watchdog_loop"
      loop_thread.daemon = True
      loop_thread.start()
  
  def main (self):
    return StatusCode.SUCCESS
  
  def loop (self):
    while (self.enabled):
      if (self._useLinuxWatchdog):
        while (self.__sendKeepAlive):
          self.__wdt_keepalive()
          if self.__resetTimers:
            self.resetTimers()
        self.warning("Watchdog stopped sending keep-alives, system will probably shutdown soon...")
        sleep(1)
      if self.__resetTimers:
        self.resetTimers()
      pass

  def finalize (self):
    self.disable()
    return StatusCode.SUCCESS

  def enable (self):
    self._enabled = True
    self.setup()

  def disable (self):
    self._enabled = False

  def addContext (self, ctx):
    self.debug("Acquiring lock for adding context")
    self.__lock.acquire()
    if ctx.name in self.__contexts:
      self.error("Context with name {} already attached to the Watchdog".format(ctx.name))
    self.__contexts[ctx.name] = ctx
    self.__lock.release()

  def getContext (self, ctx):
    if ctx in self.__contexts:
      return self.__contexts[ctx]
    else:
      self.error("Context with name {} not attached to Watchdog!".format(ctx))

  def printCollection (self):
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint (self._modules)

  def resetTimer (self, name, method, context):
    self.debug ("Resetting the {}'s method \"{}\" WDT...".format(name, method))
    try:
      self._modules[context][name][method]['wdt'].cancel()
    except KeyError:
      pass

  def startTimer (self, name, method, context):
    if context in self._modules.keys():
      if name in self._modules[context].keys():
        self.debug ("Setting the {}'s method \"{}\" WDT...".format(name, method))
        self.resetTimer(name, method, context)
        self._modules[context][name][method]['wdt'] = Timer(self._modules[context][name][method]['timeout'], self.__handler, [name, method, context])
        self._modules[context][name][method]['wdt'].start()

  def resetTimers (self):
    self.debug ("Acquiring lock for resetting")
    self.__lock.acquire()
    self.info ("Resetting all watchdog timers")
    for context in self._modules.keys():
      for key in self._modules[context].keys():
        for method in self._modules[context][key].keys():
          self.resetTimer(key, method, context)
    self.debug ("Releasing lock after resetting")
    self.__lock.release()
    self.__resetTimers = False

  def forceKeepAliveFlag (self, module):
    self.warning ("Module {} forced this Watchdog to keep sending keep-alives".format(module.name))
    self.__sendKeepAlive = True

  def enableLinuxWatchdog (self):
    self._useLinuxWatchdog = True

  def __wdt_write (self, value, count=0):
    import os
    from time import sleep
    if (count > 0):
      self.warning ("This is the retry attempt #{} to write on the WDT file".format(count + 1))
    if (count >= WDT_WRITE_ATTEMPTS):
      self.error ("Tried to write into the WDT file too many times. Rebooting system in {} seconds...".format(WDT_WRITE_FAIL_REBOOT_TIMEOUT))
      sleep(WDT_WRITE_FAIL_REBOOT_TIMEOUT)
      os.system("reboot")
    try:
      fd = os.open(WDT_FILENAME, os.O_WRONLY|os.O_NOCTTY)
      f = open(fd, WDT_FILE_OPTIONS, buffering = 0)
      f.write(value)
      f.close()
    except OSError:
      self.warning ("WDT file could not be opened, will retry in 1 second (count = {})".format(count))
      sleep(1)
      self.__wdt_write(value, count + 1)

  def __wdt_keepalive (self):
    self.__wdt_write(b".")

  def __wdt_stop (self):
    self.__wdt_write(b"V")

  def __handler (self, name, method, context):
    action = self._modules[context][name][method]['action']
    if action == "reset":
      self.getContext(context).getService(name).reset()
      self.warning ("{}'s method {} on context {} triggered the watchdog! Resetting module...".format(name, method, context))
    elif action == "terminate":
      self.__sendKeepAlive = False
      self.terminate()
      self.warning ("{}'s method {} on context {} triggered the watchdog! Shutting everything down...".format(name, method, context))
    elif action == "warn":
      self.warning ("{}'s method {} on context {} triggered the watchdog! This is a warning, as requested.".format(name, method, context))

  def terminate (self):
    for ctx in self.__contexts:
      self.__contexts[ctx].finalize()
