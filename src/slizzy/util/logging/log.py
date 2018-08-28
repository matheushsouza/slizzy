import sys

from .. import color
from . import level


class Logger:
  def __init__(self, prefix):
    self.__prefix = prefix
    self.in_progress = False
  
  
  def prefix(self, level):
    return (color.blue("[") + self.__prefix + ":" + level + color.blue("] "))
  
  
  def log(self, text, level = level.done, end = "\n"):
    if self.in_progress:
      print() # break from progress line
      self.in_progress = False
    
    print(self.prefix(level) + text, end = end)
    
    if end != "\n":
      sys.stdout.flush()
  

  def br(self):
    if self.in_progress:
      print() # break from progress line
      self.in_progress = False
    
    print()

  
  def progress(self, text, index = None):
    class Progress:
      def __init__(self, logger, text, index):
        self.logger = logger
        self.logger.in_progress = True
        self.text   = text
        self.index  = index
      
      def finish(self, text, level = None):
        self.step(text, end = True, level_ = level)
        self.logger.in_progress = False
      
      def step(self, text = None, end = False, level_ = None):
        if text or level_:
          self.text = text
          print("\033[K", end = "") # Clear the line

        if not level_:
          level_ = level.done if end else level.info

        text = self.logger.prefix(level_) + self.text
        
        if self.index and not end:
          text += color.yellow(" #" + str(self.index))
          self.index += 1
        
        print(text, end = "\n" if end else "\r")
      
    return Progress(self, text, index)


  def finish(self, text = None, level = level.done):
    if text:
      self.log(text, level)
    else:
      print()
