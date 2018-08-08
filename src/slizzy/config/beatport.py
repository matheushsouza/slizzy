import re

from . import cfg, ConfigError


__all__ = [
  "init",
  "fuzz_threshold",
  "cx"
]


def init():
  global fuzz_threshold, cx
  
  try:
    fuzz_threshold = cfg["beatport"].getint("fuzz-threshold")
    cx = cfg["beatport"]["cx"]
  except Exception as e:
    raise ConfigError() from e
  
  if not re.match(r"[0-9]{21}:[a-z0-9_]{11}", cx):
    raise ConfigError("invalid google API cx '" + cx + "'")


init()
