import itertools
import json
import re
import requests

from .. import tolerance
from ..config import slider as cfg
from ..util import color, iterator, logging, string, time, types


__all__ = [
  "slider"
]


logger = logging.Logger("slider")


base_url = "http://slider.kz"


def fetch(track):
  progress = logger.progress("Retrieving slider entries...", 1)
  
  raw_entries = 0
  while isinstance(raw_entries, int): # Slider sometimes returns error codes instead of
    progress.step()                   # the desired result.
    page = requests.get(base_url + "/vk_auth.php", params = { "q" : track.query_string })

    if page.status_code != 200:
      raise requests.exceptions.HTTPError("http code " + str(page.status_code) + ".")
    
    raw_entries = json.loads(page.content)
  
  entries = [
    types.Obj(
      id       = entry["id"],
      url      = entry["url"],
      extra    = entry["extra"],
      duration = entry["duration"],
      title    = entry["tit_art"]
    )
    for key, entries in raw_entries["audios"].items()
    for entry in entries
  ]
  
  progress.finish(
    "Retrieved " + color.result(len(entries)) + " slider " +
    ("entry." if len(entries) == 1 else "entries.")
  )
  
  return entries


def fetch_info(id, duration, info_url):
  progress = logger.progress("Fetching metadata (" + id + ")...", 1)

  attempts = 10

  for _ in range(attempts):
    progress.step()
    
    page = requests.get(info_url)
    
    if page.status_code != 200:
      progress.finish(
        "Failed to fetch metadata: http code " + str(page.status_code) + ".",
        level = logging.level.warn
      )
      return None
    
    lines = re.sub(r"</?b>", "", page.text).split("<br>") # remove unwanted tags.
    
    try:
      data = types.Obj(
        bitrate = string.read_int(lines[0]),
        size    = (string.read_float(lines[1]), lines[1].split()[-1]) # Size, multiplier.
      )

      if data.bitrate:
        progress.finish(
          "Fetched metadata ({}): duration = {}; bitrate = {}; size = {} {};".format(
            id,
            time.to_str(duration),
            data.bitrate,
            *data.size
          )
        )
        return data

    except Exception as e:
      progress.finish(
        "Failed to fetch metadata: parse error.",
        level = logging.level.warn
      )
      return None

  progress.finish(
    "Failed to retrieve metadata after " + str(attempts) + " attempts.",
    level = logging.level.warn
  )
  return None


def normalize(entries):
  def norm(e):
    info = fetch_info(
      e.id,
      e.duration,
      "{}/info/{}/{}/{}.mp3?extra={}".format(base_url, e.id, e.duration, e.url, e.extra)
    )
    
    return types.Obj(
      id       = e.id,
      title    = e.title,
      duration = e.duration,
      bitrate  = info and info.bitrate,
      size     = info and info.size,
      download = "{}/download/{}/{}/{}/{}.mp3?extra={}".format(
        base_url,
        e.id,
        e.duration,
        e.url, 
        e.title,
        e.extra
      )
    )
  
  return [ norm(entry) for entry in entries ]


def select(entries, track):
  entries = (
    entry for entry in entries
          if entry.duration in tolerance.duration(track.duration)   # Filter by duration.
             and entry.size and entry.bitrate in tolerance.bitrate  # Filter by bitrate.
  )

  # Filter by name:
  entries, filtered = iterator.partition(
    lambda entry: string.fuzz_match(entry.title, track.title) > cfg.fuzz_threshold,
    entries
  )

  if filtered:
    logger.log(
      "Filtered {} {} by name:\n".format(
        len(filtered),
        ("entry" if len(filtered) == 1 else "entries")
      ) +
      "\n".join(
        "  " + entry.title
        for entry in filtered
      )
    )

  logger.log(
    "Selected {} {}{}".format(
      color.result(len(entries)),
      ("entry" if len(entries) == 1 else "entries"),
      (":\n" if entries else ".")
    ) +
    "\n".join(
      "\n".join([
        "Track: " + entry.title,
        "  duration : " + time.to_str(entry.duration),
        "  size     : {} {}".format(*entry.size),
        "  bitrate  : {} kbps".format(entry.bitrate),
        "  link     : {}".format(entry.download)
      ])
      for entry in entries
  ))
  
  return entries


def slider(track):
  """Returns a list of entries containing: name, link"""
  logger.log("Running slider for track '" + track.query_string + "'.", logging.level.info)

  try:
    return [
      types.Obj(
        name = entry.title,
        link = entry.download
      )
      for entry in select(normalize(fetch(track)), track)
    ]
  except Exception as e:
    logger.log("Slider failed: " + str(e), logging.level.error)
    return []
  finally:
    logger.finish()
