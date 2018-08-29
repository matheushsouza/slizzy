import re
import requests
import json

from .. import tolerance
from ..config import slider as cfg
from ..util import color, iterator, logging, string, time, types


__all__ = [
  "slider"
]


logger = logging.Logger("slider")


base_url = "http://slider.kz"


def fetch_info(info):
  progress = logger.progress("Fetching metadata (" + info + ")", 1)

  result = {
    "bitrate" : 0,
    "size"    : (0, "") # Size, multiplier.
  }
  while not result["bitrate"]:
    progress.step()
    
    page = requests.get(base_url + info)

    if page.status_code != 200:
      progress.finish(
        "Failed to fetch metadata: http code " + str(page.status_code) + ".",
        level = logging.level.warn
      )
      return None
    
    lines = re.sub(r"</?b>", "", page.text).split("<br>") # remove unwanted tags.
    
    try:
      result = {
        "bitrate" : string.read_int(lines[0]),
        "size"    : (string.read_float(lines[1]), lines[1].split()[-1]) # Size, multiplier.
      }
    except Exception as e:
      logger.error("failed to retrieve track info.")
      raise ValueError(lines) from e
  
  progress.finish("Fetched metadata: {} ({})".format(result, info))
  
  return result


def fetch_entries(track):
  progress = logger.progress("Retrieving slider entries", 1)
  
  raw_entries = 0
  while isinstance(raw_entries, int): # Slider sometimes returns error codes instead of
    progress.step()                   # the desired result.
    page = requests.get(base_url + "/vk_auth.php", params = { "q" : track.query_string })

    if page.status_code != 200:
      raise requests.exceptions.HTTPError("http code " + str(page.status_code) + ".")
    
    raw_entries = json.loads(page.content)
  
  entries = [
    obj["entry"]
    for obj in raw_entries["feed"]
  ]

  progress.finish(
    "Retrieved " + color.result(len(entries)) + " slider " +
    ("entry." if len(entries) == 1 else "entries.")
  )
  
  return entries


def filter_entries(entries, track):
  # Filter by duration:
  entries = filter(
    lambda e: e["duration"] in tolerance.duration(track.duration),
    entries
  )

  # Filter by name:
  entries, filtered = iterator.partition(
    lambda e: string.fuzz_match(e["tit_art"], track.name) > cfg.fuzz_threshold,
    entries
  )

  if filtered:
    logger.log(
      "Filtered {} {} by name:\n".format(
        len(filtered),
        ("entry" if len(filtered) == 1 else "entries")
      ) +
      "\n".join(
        "  " + entry["tit_art"]
        for entry in filtered
      )
    )

  # Filter by bitrate:
  entries = [
    {
      "title"    : entry["tit_art"],
      "duration" : entry["duration"],
      "size"     : info["size"],
      "bitrate"  : info["bitrate"],
      "download" : base_url + entry["url"]
    }
    for entry in entries
    for info in [ fetch_info(entry["info_url"]) ]
    if info and info["bitrate"] in tolerance.bitrate
  ]
  
  logger.log(
    "Selected {} {}{}".format(
      color.result(len(entries)),
      ("entry" if len(entries) == 1 else "entries"),
      (":\n" if entries else ".")
    ) +
    "\n".join(
      "\n".join([
        "Track: " + entry["title"],
        "  duration : " + time.to_str(entry["duration"]),
        "  size     : " + "{} {}".format(*entry["size"]),
        "  bitrate  : " + str(entry["bitrate"]) + " kbps",
        "  link     : " + str(entry["download"])
      ])
      for entry in entries
  ))
  
  return entries


def slider(track):
  """Returns a list of entries containing: url, title, duration, size, bitrate"""
  logger.log("Running slider for track '" + track.query_string + "'.", logging.level.info)

  try:
    return [
      types.Obj(
        name = entry["title"],
        link = entry["download"]
      )
      for entry in filter_entries(fetch_entries(track), track)
    ]
  except Exception as e:
    logger.log("Slider failed: " + str(e), logging.level.error)
    return []
  finally:
    logger.finish()
