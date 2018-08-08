import sys

from .configerror import ConfigError
from .setup import setup, load, update


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
  setup()
  cfg = load()
except Exception as e:
  print("Error (config): " + str(e), file = sys.stderr)
  sys.exit(2)
