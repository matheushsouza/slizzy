import re

from . import cfg, ConfigError


__all__ = [
  "init",
  "fuzz_threshold",
  "cx",
  "blacklist"
]


def init():
  global fuzz_threshold, cx, blacklist

  try:
    fuzz_threshold = cfg["zippyshare"].getint("fuzz-threshold")
    cx = cfg["zippyshare"]["cx"]
    blacklist = [
      stripped
      for item in cfg["zippyshare"]["blacklist"].splitlines()
      for stripped in [ item.strip() ]
      if stripped # Ignore blank entries.
    ]
  except Exception as e:
    raise ConfigError() from e

  if not re.match(r"[0-9]{21}:[a-z0-9_]{11}", cx):
    raise ConfigError("invalid google API cx '" + cx + "'")


init()
