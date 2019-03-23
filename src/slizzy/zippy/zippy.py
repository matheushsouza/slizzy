import math
import re
import requests
from bs4          import BeautifulSoup
from functools    import reduce
from urllib.parse import urlparse

from .. import tolerance
from ..config import zippy as cfg
from ..util   import logging, math as math_util, mp3, string, time, types
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


expired_label = r"File.* does not exist.* on this server"


def fetch_page(url, key):
  progress = logger.progress("Fetching page (" + key + ")...")
  progress.step()
  
  page = requests.get(url.geturl())
  
  if page.status_code != 200:
    raise requests.exceptions.HTTPError("http code " + str(page.status_code) + ".")
  
  progress.finish("Fetched page (" + key + ").")

  return page


def scrap(url, key, page):
  progress = logger.progress("Scrapping page (" + key + ")...")
  progress.step()

  scrapper = BeautifulSoup(page.content, "html.parser")

  if scrapper.find("div", text = re.compile(expired_label)):
    raise ValueError("Expired file.")

  if scrapper.find("img", src = re.compile(r"^/fileName\?key=")):
    title = None
  else:
    title = scrapper.find("font", text = re.compile("Name: ?")).find_next("font").text

  size = string.read_number(
    scrapper.find("font", text = re.compile("Size: ?")).find_next("font").text
  )

  download = scrap_download(url, scrapper)
  
  progress.finish("Scrapped page: " + (title if title else "private download."))
  
  return title, size, download


def scrap_download(url, scrapper):
  # The download script is something in the format:
  # <script type="text/javascript">
  #     var a = 761204;
  #     var b = 742589;
  #     document.getElementById('dlbutton').omg = "f";
  #     if (document.getElementById('dlbutton').omg != 'f') {
  #        a = Math.ceil(a/3);
  #     } else {
  #        a = Math.floor(a/3);
  #     }
  #     document.getElementById('dlbutton').href = "/d/NZCSsATl/"+(a + 761204%b)+"/Pional%20-%20Tempest%20%28Original%20Mix%29%20%5bClapCrate.me%5d.mp3";
  #     if (document.getElementById('fimage')) {
  #         document.getElementById('fimage').href = "/i/NZCSsATl/"+(a + 761204%b)+"/Pional%20-%20Tempest%20%28Original%20Mix%29%20%5bClapCrate.me%5d.mp3";
  #     }
  # </script>
  download_code_re = r"document\.getElementById\('dlbutton'\)\.href ?= ?"

  script = scrapper.find("script", text = re.compile(download_code_re)).text

  href = re.search(
    r"^ +" + download_code_re + r"(.+); *$",
    script,
    re.MULTILINE
  ).group(1)

  numbers = [ int(n) for n in re.findall(r"\d+", script)[:2] ]

  var_a = math.floor(numbers[0]/3)
  var_b = numbers[1]

  result = "".join([
    str(
      string.literal(node) if '"' in node
      else math_util.eval(
          node.replace("a", str(var_a)) \
              .replace("b", str(var_b))
      )
    )
    for node in re.split(r"\++(?=[^()]*(?:\(|$))", href) # Split on unparenthesised +
  ])
  
  return url.scheme + "://" + url.netloc + result


def fetch_duration(url, key):
  progress = logger.progress("Fetching duration (" + key + ")...")
  progress.step()

  # This is a compressed file, so the bitrate is always 64 kbps.
  info = mp3.fetch_info(url.scheme + "://" + url.netloc + "/downloadMusicHQ?key=" + key)
  
  progress.finish("Fetched duration ({}): {}".format(key, time.to_str(info.duration)))
  
  return info.duration


def get_download(track, url):
  logger.log("Running zippyshare scrapper for page " + url, logging.level.info)
  
  try:
    url = urlparse(url)
    key = url.path.split("/")[2]

    title, size, download = scrap(url, key, fetch_page(url, key))
    
    if title:
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
    
    duration = fetch_duration(url, key)
    if duration not in tolerance.duration(track.duration):
      raise ValueError("Duration mismatch: {}/{}.".format(
        time.to_str(duration),
        time.to_str(track.duration)
      ))

    if size not in tolerance.size(duration):
      raise ValueError("Size mismatch: {} mb / {}.".format(size, time.to_mins(duration)))

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
