import re
import requests
from bs4          import BeautifulSoup
from functools    import reduce
from hsaudiotag   import mp4
from io           import BytesIO
from urllib.parse import urlparse

from .. import tolerance
from ..config import zippy as cfg
from ..util   import logging, math, string, time, types
from ..google import Domain


__all__ = [
  "domain",
  "get_download"
]


domain = Domain(
  "zippyshare",
  r"^https://www\d*\.zippyshare\.com/.*",
  cfg.cx
)


logger = logging.Logger("zippy")


expired_label = "File has expired and does not exist anymore on this server"


def fetch_page(url, key):
  progress = logger.progress("Fetching page (" + key + ").")
  progress.step()
  
  page = requests.get(url.geturl())
  
  if page.status_code != 200:
    raise requests.exceptions.HTTPError("http code " + str(page.status_code) + ".")
  
  progress.finish("Fetched page (" + key + ").")

  return page


def scrap(url, key, page):
  progress = logger.progress("Scrapping page (" + key + ").")
  progress.step()

  scrapper = BeautifulSoup(page.content, "html.parser")

  if scrapper.find("div", text = expired_label):
    raise ValueError("Expired file.")

  if scrapper.find("img", src = re.compile(r"^/fileName\?key=")):
    title = None
  else:
    title = scrapper.find("font", text = re.compile("Name: ?")).find_next("font").text

  download = scrap_download(url, scrapper)
  
  progress.finish("Scrapped page: " + (title if title else "private download."))
  
  return title, download


def scrap_download(url, scrapper):
  # The download script is something in the format:
  # <script type="text/javascript">
  #   document.getElementById('dlbutton').href = "/d/<key>/" + (852443 % 51245 + 852443 % 913) + "/{...}.mp3";
  #   ...
  # </script>
  download_code_re = r"document\.getElementById\('dlbutton'\)\.href ?= ?"
  
  script = re.search(
    r"^ +" + download_code_re + r"(.+); *$",
    scrapper.find("script", text = re.compile(download_code_re)).text,
    re.MULTILINE
  ).group(1)
  
  result = reduce(
    lambda acc, node: acc + str(string.literal(node) if '"' in node else math.eval(node)),
    re.split(r"\++(?=[^()]*(?:\(|$))", script), # Split on unparenthesised +
    ""
  )
  
  return url.scheme + "://" + url.netloc + result


def fetch_info(url, key):
  progress = logger.progress("Fetching metadata (" + key + ").")
  progress.step()

  page = requests.get(
    url.scheme + "://" + url.netloc + "/downloadMusicHQ?key=" + key,
    headers = { "Range" : "bytes=0-512" } # The first 512 bytes are sufficient for
  )                                       # extracting the metadata.

  if page.status_code not in [ 200, 206 ]: # 206 = partial content
    raise requests.exceptions.HTTPError("http code " + str(page.status_code) + ".")

  with BytesIO(page.content) as bs:
    # This is a compressed file, so the bitrate is always 64 kbps.
    duration = mp4.File(bs).duration
  
  progress.finish("Fetched duration: " + time.to_str(duration))
  
  return duration


def get_download(track, url):
  logger.log("Zippyshare scrapper for page " + url, logging.level.info)
  
  try:
    url = urlparse(url)
    key = url.path.split("/")[2]

    title, download = scrap(url, key, fetch_page(url, key))
    
    if string.fuzz_match(title, track.title) < cfg.fuzz_threshold:
      raise ValueError("track name mismatch: ('{}', '{}')[{}] below [{}].".format(
        title,
        track.title,
        string.fuzz_match(title, track.title),
        cfg.fuzz_threshold
      ))
    
    blacklisted = next(
      (bl
       for bl in cfg.blacklist
       if re.search(bl, title, re.IGNORECASE)),
      None
    )
    if blacklisted:
      raise ValueError("track name blacklisted by '{}': '{}'.".format(blacklisted, title))
    
    duration = fetch_info(url, key)
    
    if duration not in tolerance.duration(track.duration):
      raise ValueError("Duration mismatch: {}/{}.".format(
        time.to_str(duration),
        time.to_str(track.duration)
      ))

    logger.log("Selected download: " + download, logging.level.done)
    
    return types.Obj(name = title, link = download)
  
  except ValueError as e:
    logger.log(str(e), logging.level.error)
    return None
  
  except Exception as e:
    logger.log("Zippyshare scrapper failed: " + str(e), logging.level.error)
    return None
  
  finally:
    logger.finish()
