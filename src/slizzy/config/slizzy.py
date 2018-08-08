from . import cfg, ConfigError


__all__ = [
  "init",
  "duration_tolerance",
  "bitrate_min"
]


def init():
  global duration_tolerance, bitrate_min

  try:
    duration_tolerance = cfg["slizzy"].getint("duration-tolerance")
    bitrate_min = cfg["slizzy"].getint("bitrate-min")
  except Exception as e:
    raise ConfigError() from e


init()
