from . import cfg, ConfigError


__all__ = [
  "init",
  "fuzz_threshold"
]


def init():
  global fuzz_threshold

  try:
    fuzz_threshold = cfg["mp3co"].getint("fuzz-threshold")
  except Exception as e:
    raise ConfigError() from e


init()
