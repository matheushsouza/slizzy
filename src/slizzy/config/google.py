import re

from . import cfg, ConfigError


__all__ = [
  "init",
  "key"
]


def init():
  global key

  try:
    key = cfg["google"]["key"]
  except Exception as e:
    raise ConfigError() from e
  
  if not re.match(r"AIza.{35}", key):
    raise ConfigError("invalid google API key '" + key + "'")


init()
