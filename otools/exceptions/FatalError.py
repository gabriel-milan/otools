__all__ = ['FatalError']

class FatalError (RuntimeError):

  def __str__ (self):
    return "<OTools FatalError>"

  def __repr__ (self):
    return self.__str__()