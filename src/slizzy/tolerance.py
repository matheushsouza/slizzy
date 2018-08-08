from .config import slizzy as cfg


def duration(duration):
  return range(
    duration - cfg.duration_tolerance,
    duration + cfg.duration_tolerance + 1
  )


bitrate = range(cfg.bitrate_min, 1000000) # absurd upper bound.
