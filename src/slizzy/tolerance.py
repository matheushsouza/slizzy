from .config import slizzy as cfg
from .util   import frange, time


def duration(duration):
  return range(
    duration - cfg.duration_tolerance,
    duration + cfg.duration_tolerance + 1
  )


def size(duration): # duration: seconds
  return frange(
    (time.to_mins(duration) * cfg.size_factor) - cfg.size_tolerance,
    (time.to_mins(duration) * cfg.size_factor) + cfg.size_tolerance
  )


bitrate = range(cfg.bitrate_min, 1000000) # absurd upper bound.
