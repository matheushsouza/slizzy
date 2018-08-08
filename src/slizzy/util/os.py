import os


def oserror(errno, filename = None):
  return OSError(errno, os.strerror(errno), filename)



class Umask:
  def __init__(self, umask):
    self.umask = umask
    self.old_umask = None

  
  def __enter__(self):
    self.old_umask = os.umask(self.umask)


  def __exit__(self, ex_type, ex_value, traceback):
    os.umask(self.old_umask)
