__all__ = [
  'SECOND',
  'MINUTE',
  'HOUR',
  'DAY',
  'WEEK',
  'DEFAULT_METHOD_DICT',
  'ACCEPTED_ACTIONS',
  'ACCEPTED_METHODS',
  'WDT_WRITE_ATTEMPTS',
  'WDT_FILENAME',
  'WDT_FILE_OPTIONS',
  'WDT_WRITE_FAIL_REBOOT_TIMEOUT'
]

# Time constants
SECOND  = 1
MINUTE  = 60 * SECOND
HOUR    = 60 * MINUTE
DAY     = 24 * HOUR
WEEK    = 7 * DAY

# Watchdog
DEFAULT_METHOD_DICT = {
  'enable'      : True,
  'timeout'     : 10 * SECOND,
  'action'      : 'reset'
}
ACCEPTED_ACTIONS                = ['reset', 'terminate', 'warn']
ACCEPTED_METHODS                = ['main', 'loop']
WDT_WRITE_ATTEMPTS              = 5
WDT_FILENAME                    = '/dev/watchdog'
WDT_FILE_OPTIONS                = 'wb+'
WDT_WRITE_FAIL_REBOOT_TIMEOUT   = 5
