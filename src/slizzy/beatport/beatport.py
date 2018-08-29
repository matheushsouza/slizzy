import requests
from bs4 import BeautifulSoup

from ..config import beatport as cfg
from ..google import Domain
from ..util import logging, string, time


__all__ = [
  "domain",
  "get_metadata"
]


domain = Domain(
  "beatport",
  r"^https://www.beatport.com/track/.*",
  cfg.cx
)


logger = logging.Logger("beatport")


def scrap(url):
  progress = logger.progress("Fetching page.")
  progress.step()
  
  page = requests.get(url)
  
  if page.status_code != 200:
    raise requests.exceptions.HTTPError("http code " + str(page.status_code) + ".")
  
  progress.step("Scrapping page.")
  
  scrapper = BeautifulSoup(page.content, "html.parser")
  
  length = scrapper.find(
    "li",
    { "class" : "interior-track-length" }
  ).find(
    "span",
    { "class" : "value" }
  ).text.split(":")
  length = int(length[0]) * 60 + int(length[1])
  
  name = scrapper.find(
    "div",
    { "class" : "interior-title" }
  ).find(
    "h1"
  ).text
  
  progress.finish("Fetched metadata:\n  name   : {}\n  length : {}".format(
    name,
    time.to_str(length)
  ))
  
  return (name, length)


def get_metadata(track, url):
  logger.log("Beatport scrapper for page " + url, logging.level.info)
  
  try:
    name, duration = scrap(url)
    
    if string.fuzz_match(name, track.name) < cfg.fuzz_threshold:
      raise ValueError("track name mismatch: ('{}', '{}')[{}] below [{}].".format(
        name,
        track.name,
        string.fuzz_match(name, track.name),
        cfg.fuzz_threshold
      ))
    
    return duration

  except ValueError as e:
    logger.log(str(e), logging.level.error)
    return None

  except Exception as e:
    logger.log("Beatport scrapper failed: " + str(e), logging.level.error)
    return None
  
  finally:
    logger.finish()
