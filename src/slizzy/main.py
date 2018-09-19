#!/usr/bin/env python3

import argparse
import enum
import sys

import slizzy.config  as config
import slizzy.version as version
from slizzy.track     import Track
from slizzy.util      import color, logging, time


__all__ = [
  "module",
  "all_modules",
  "slizzy"
]


module = enum.Enum("modules", "slider mp3co zippy")
all_modules = { module.slider, module.mp3co, module.zippy }



def slizzy(track, modules, download_tracks):
  logger = logging.Logger("slizzy")

  logger.log("Slizzy magic for track '" + track.title + "'", logging.level.info)
  logger.log("Query string: " + track.query_string, logging.level.info)
  logger.br()

  
  if not track.duration: # Duration not supplied from command line.
    try:
      from slizzy.google   import google
      from slizzy.beatport import beatport
      
      track.duration = next( # Extract duration from the first matching page.
        duration
        for page     in google(track, beatport.domain)
        for duration in [ beatport.get_metadata(track, page) ]
        if duration
      )
    except StopIteration:
      logger.log("Track duration unavailable", logging.level.error)
      return
  
  
  if module.slider in modules:
    from slizzy.slider import slider
    
    slider_downloads = slider(track)
  else:
    slider_downloads = []


  if module.mp3co in modules:
    from slizzy.mp3co import mp3co
    
    mp3co_downloads = mp3co(track)
  else:
    mp3co_downloads = []
  
  
  if module.zippy in modules:
    from slizzy.google import google
    from slizzy.zippy  import zippy
    
    zippy_downloads = [
      dl
      for page in google(track, zippy.domain)
      for dl   in [ zippy.get_download(track, page) ]
      if dl
    ]
  else:
    zippy_downloads = []


  if module.slider in modules:
    logger.log(
      "Selected " + color.result(len(slider_downloads)) + " slider entries.",
      logging.level.info
    )
  
  if module.mp3co in modules:
    logger.log(
      "Selected " + color.result(len(mp3co_downloads)) + " mp3co entries.",
      logging.level.info
    )
  
  if module.zippy in modules:
    logger.log(
      "Selected " + color.result(len(zippy_downloads)) + " zippy entries.",
      logging.level.info
    )

  
  downloads = slider_downloads + mp3co_downloads + zippy_downloads
  
  if not downloads:
    logger.log("No entries to download.")
    return
  
  if download_tracks:
    from slizzy.downloader import download
      
    download(downloads)
  else:
    logger.log("Selected urls:\n  " + "\n  ".join(
      download.name + " | " + download.link
      for download in downloads
    ))
  
  logger.br()
  logger.finish("Slizzied " + str(len(downloads)) + " files.")



def parse_args(argv):
  parser = argparse.ArgumentParser(
    description = "Slizzy is a tool to search for and "
                  "download slider.kz, mp3co.biz and zippyshare objects.",
    formatter_class = argparse.RawTextHelpFormatter
  )
  parser.add_argument(
    "--version", "-v",
    action = "version",
    version = "\n".join([
      "%(prog)s " + version.__version__,
      "Copyright (c) 2018, gahag.",
      "All rights reserved."
    ])
  )
  commands = parser.add_subparsers(dest = "command", help = "commands")

  dl  = commands.add_parser("dl",  help="download tracks")
  lns = commands.add_parser("lns", help="get download links")
  cfg = commands.add_parser("cfg", help="config")
  
  for command in [ dl, lns ]:
    command.add_argument(
      "tracks",
      help = "one or more tracks to seach, in the format: "
             "A & B ft. C - ID (D vs. E Remix)",
      nargs = "+"
    )
    command.add_argument(
      "-d", "--duration",
      help = "manually specify the track duration, eliding the beatport search"
    )
    command.add_argument(
      "--slider",
      action = "store_true",
      help = "search in slider.kz instead of all resources"
    )
    command.add_argument(
      "--mp3co",
      action = "store_true",
      help = "search in mp3co.biz instead of all resources"
    )
    command.add_argument(
      "--zippy",
      action = "store_true",
      help = "search only in zippyshare instead of all resources"
    )
  
  cfg.add_argument("--google-key", help = "set the google API key")
  cfg.add_argument("--beatport-cx", help = "set the cx API key for the beatport search")
  cfg.add_argument("--zippyshare-cx", help = "set the cx API key for the zippyshare search")
  # add arguments for other settings, specially thresholds.


  if not argv:
    parser.print_usage()
    sys.exit(1)
  
  args = parser.parse_args(argv)

  if args.command in [ "dl", "lns" ]:
    if args.duration:
      if len(args.tracks) > 1:
        print(
          "Error: with the duration parameter, only one track may be specified.",
          file = sys.stderr
        )
        sys.exit(1)
  
      try:
        args.duration = time.from_str(args.duration)
      except Exception as e:
        print("Error: " + str(e) + ".", file = sys.stderr)
        sys.exit(1)

  if args.command == "cfg":
    pass # validate args
  
  return args



def main(argv):
  args = parse_args(argv)
  
  if args.command in [ "dl", "lns" ]:
    for i, track in enumerate(args.tracks):
      try:
        args.tracks[i] = Track(track, args.duration)
      except:
        print("Error: invalid track format '" + track + "'.", file = sys.stderr)
        sys.exit(1)
    
    modules = {
      m
      for m, arg in [
        (module.slider, args.slider),
        (module.mp3co, args.mp3co),
        (module.zippy,  args.zippy)
      ]
      if arg
    } or all_modules

    download_tracks = args.command == "dl"

    tracks = iter(args.tracks)
    
    try:
      slizzy(next(tracks), modules, download_tracks)
      
      for track in tracks:
        print(color.yellow(70 * "-"))
        slizzy(track, modules, download_tracks)
    except config.ConfigError as e:
      print("Error (config): " + str(e), file = sys.stderr)
      sys.exit(2)
  
  
  if args.command == "cfg":
    if args.google_key:
      config.cfg["google"]["key"] = args.google_key
      
    if args.beatport_cx:
      config.cfg["beatport"]["cx"] = args.beatport_cx

    if args.zippyshare_cx:
      config.cfg["zippyshare"]["cx"] = args.zippyshare_cx
    
    try:
      config.update(config.cfg)
    except config.ConfigError as e:
      print("Error (config): " + str(e), file = sys.stderr)
      sys.exit(2)



def cli():
  import signal
  
  def sigint(sig, frame):
    print() # Exit progress logging
    print("Slizzy: interrupted.", file = sys.stderr)
    sys.exit(130)

  signal.signal(signal.SIGINT, sigint)
  
  main(sys.argv[1:])
