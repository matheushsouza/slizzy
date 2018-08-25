import json
import re
import requests

from ..config import google as cfg
from ..util import color, logging


__all__ = [
  "Domain",
  "google"
]


class Domain:
  def __init__(self, name, regex, cx):
    self.name  = name
    self.regex = re.compile(regex)
    self.cx = cx


logger = logging.Logger("google")


def fetch(query, domain):
  progress = logger.progress("Fetching search for '" + query + "'.")
  progress.step()
  
  page = requests.get(
    "https://www.googleapis.com/customsearch/v1",
    params = {
      "q"   : query,
      "key" : cfg.key,
      "cx"  : domain.cx
    }
  )
  
  if page.status_code != 200:
    raise requests.exceptions.HTTPError("http code " + str(page.status_code) + ".")

  try:
    search = json.loads(page.text)["items"]
  except Exception as e:
    raise ValueError("failed to obtain results.") from e
  
  progress.finish("Retrieved " + color.result(len(search)) + " search results.")

  filtered = list(
    filter(
      domain.regex.match,
      (item['link'] for item in search)
    )
  )
  
  logger.log("Selected " + color.result(len(filtered)) + " search results.")
  
  return filtered


def google(track, domain):
  logger.log(
    "Google search at " + domain.name + ".",
    logging.level.info
  )

  try:
    return fetch(track.query_string, domain)
  except Exception as e:
    logger.log("Google failed: " + str(e), logging.level.error)
    return []
  finally:
    logger.finish()
