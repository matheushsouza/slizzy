import os.path
import threading


__all__ = [
  "sanitize",
  "unused_filename"
]


lock = threading.Lock()


def sanitize(filename):
  return filename.replace("/", "").replace("\"", "")


def unused_filename(filename):
  lock.acquire()
  
  if os.path.exists(filename):
    filename, ext = os.path.splitext(filename)
    
    i = 1
    while os.path.exists(filename + " (" + str(i) + ")" + ext):
      i += 1

    filename = filename + " (" + str(i) + ")" + ext
    
    open(filename, "a").close() # Touch the file, so subsequent calls to this function
                                # won't result in the same file name.

  lock.release()
  
  return filename
