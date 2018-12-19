import cgi
import requests
import time
import threading

from ..util import path 


__all__ = [
  "download"
]


class Progress:
  def __init__(self, filename = None):
    self.filename   = filename
    self.filesize   = None
    self.downloaded = 0
    self.started  = False
    self.canceled = False


  def start(self):
    self.started = True

  
  def finish(self):
    self.filesize = self.downloaded

  
  def cancel(self):
    self.canceled = True

  
  def finished(self):
    return self.downloaded == self.filesize
    
  
  def __str__(self):
    if not self.started:
      return "Starting download... | " + (self.filename if self.filename else "?")
    
    if self.canceled:
      return "CANCELED | " + (self.filename if self.filename else "?") + "\033[K"

    if self.finished():
      return "Done ({:4.1f}MB) | {}\033[K".format(
        self.downloaded / 1048576.0,
        self.filename
      )

    if self.filesize:
      return "{:3}% ({:4.1f}MB of {:4.1f}MB) | {}".format(
        int(self.downloaded * 100.0 / self.filesize),
        self.downloaded / 1048576.0,
        self.filesize   / 1048576.0,
        self.filename
      )

    return " ? % ({:4.1f}MB of     ? MB) | {}".format(
      self.downloaded / 1048576.0,
      self.filename
    )



def __download(dl):
  dl.page = requests.get(dl.link, stream = True)

  if dl.page.status_code != 200:
    raise requests.exceptions.HTTPError("http code " + str(dl.page.status_code) + ".")

  try:
    filename = cgi.parse_header(dl.page.headers.get("Content-Disposition"))[1]["filename"]
  except:
    filename = None
  
  dl.progress.filename = path.unused_filename(path.sanitize(filename or dl.name))

  try:
    dl.progress.filesize = int(dl.page.headers["Content-Length"])
  except:
    dl.progress.filesize = None
  
  dl.progress.start()
  
  with open(dl.progress.filename, 'wb') as out:
    buffer_size = 8192
    for chunk in dl.page.iter_content(chunk_size = buffer_size):
      # if chunk: # filter out keep-alive new chunks
      out.write(chunk)
      dl.progress.downloaded += len(chunk)

    dl.progress.finish()



def download(downloads):
  for dl in downloads:
    dl.progress = Progress()
    dl.thread = threading.Thread(target = __download, args = (dl,))
    dl.thread.start()
  
  back = "\033[" + str(len(downloads)) + "A"

  while threading.activeCount() > 1:
    for dl in downloads:
      print(dl.progress)
    
    print(back, end = "")
    
    time.sleep(0.5)
  
  for download in downloads:
    print(download.progress)
