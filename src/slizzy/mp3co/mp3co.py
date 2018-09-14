import requests
from bs4 import BeautifulSoup

from .. import tolerance
from ..config import mp3co as cfg
from ..util import bytes, color, iterator, logging, string, time, types


__all__ = [
  "mp3co"
]


logger = logging.Logger("mp3co")


base_url = "https://mp3co.biz"


def fetch_size(id, download):
  progress = logger.progress("Fetching file size (" + id + ")...")
  progress.step()

  try:
    page = requests.head(download)

    if page.status_code != 200:
      raise requests.exceptions.HTTPError("http code " + str(page.status_code) + ".")

    size = int(page.headers["content-length"])
    
    progress.finish("Fetched file size ({}): {:.2f} mb".format(id, bytes.to_MB(size)))
    
    return size
  
  except Exception as e:
    progress.finish(
      "Failed to fetch file size({}): {}".format(id, e),
      level = logging.level.warn
    )
    return None


def fetch_entries(track):
  progress = logger.progress("Retrieving mp3co entries...")
  progress.step()
  
  page = requests.get(base_url + "/s/" + track.query_string)
  
  if page.status_code != 200:
    raise requests.exceptions.HTTPError("http code " + str(page.status_code) + ".")
  
  progress.step("Scrapping mp3co entries...")
  
  scrapper = BeautifulSoup(page.content, "html.parser")
  songs = scrapper.find("table", class_ = "songs")
  
  entries = [
    types.Obj(
      id       = song["id"],
      title    = artist.text + " - " + name.text,
      duration = time.from_str(song.find("td", class_ = "time").text),
      download = song.find("a", class_ = "i-dl")["href"]
    )
    for song in songs.find_all("tr", recursive = False)
    for [ artist, name ] in [ song.find("td", class_ = "name").find_all("a") ]
  ]
  
  progress.finish(
    "Retrieved " + color.result(len(entries)) + " mp3co " +
    ("entry." if len(entries) == 1 else "entries.")
  )
  
  return entries


def filter_entries(entries, track):
  # Filter by duration:
  entries = filter(
    lambda e: e.duration in tolerance.duration(track.duration),
    entries
  )

  # Filter by name:
  entries, filtered = iterator.partition(
    lambda e: string.fuzz_match(e.title, track.title) > cfg.fuzz_threshold,
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

  # Filter by bitrate:
  entries = [
    types.Obj(
      id       = entry.id,
      title    = entry.title,
      duration = entry.duration,
      size     = size,
      download = entry.download
    )
    for entry in entries
    for size in [ fetch_size(entry.id, entry.download) ]
    if size and bytes.to_MB(size) in tolerance.size(entry.duration)
  ]
  
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
        "  size     : {} mb".format(bytes.to_MB(entry.size)),
        "  link     : " + str(entry.download)
      ])
      for entry in entries
  ))
  
  return entries


def mp3co(track):
  """Returns a list of entries containing: name, link"""
  logger.log("Running mp3co for track '" + track.query_string + "'.", logging.level.info)

  try:
    return [
      types.Obj(
        name = entry.title,
        link = entry.download
      )
      for entry in filter_entries(fetch_entries(track), track)
    ]
  except Exception as e:
    logger.log("Mp3co failed: " + str(e), logging.level.error)
    return []
  finally:
    logger.finish()
