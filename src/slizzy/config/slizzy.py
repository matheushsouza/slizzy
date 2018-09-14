from . import cfg, ConfigError


__all__ = [
  "init",
  "duration_tolerance",
  "bitrate_min"
]


def init():
  global duration_tolerance, bitrate_min, size_factor, size_tolerance

  try:
    duration_tolerance = cfg["slizzy"].getint("duration-tolerance")
    bitrate_min        = cfg["slizzy"].getint("bitrate-min")
    size_factor        = cfg["slizzy"].getfloat("size-factor")
    size_tolerance     = cfg["slizzy"].getfloat("size-tolerance")
  except Exception as e:
    raise ConfigError() from e


init()
