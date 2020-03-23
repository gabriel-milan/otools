__all__ = [
  'StatusCode'
]

class StatusObject ():

  status = 1

  def __init__ (self, status):
    self.status = status

  def isFailure (self):
    return self.status < 0
  
  def __eq__ (self, a):
    return self.status == a.status

  def __ne__ (self, a):
    return self.status != a.status

class StatusCode ():
  """
  General purpose status code
  """
  SUCCESS = StatusObject(0)
  FAILURE = StatusObject(-1)
  FATAL   = StatusObject(-2)