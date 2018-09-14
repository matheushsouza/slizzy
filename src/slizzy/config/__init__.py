import sys

from .configerror import ConfigError
from .setup import setup, update


__all__ = [
  "ConfigError,"
  "cfg",
  "update",
  "slizzy",
  "google",
  "beatport",
  "slider",
  "zippy"
]


try:
  cfg = setup()
except ConfigError as e:
  print("Error (config): " + str(e), file = sys.stderr)
  sys.exit(2)
