def auto_str(cls):
  def __str__(self):
    return type(self).__name__ + "\n" + "\n".join(
      "  %s = %s" % field
      for field in vars(self).items()
    )
  cls.__str__ = __str__
  cls.__repr__ = __str__
  return cls


@auto_str
class Obj(object):
  def __init__(self, **kwargs):
    self.__dict__.update(kwargs)
