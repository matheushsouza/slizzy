import time


__all__ = [
  "from_str",
  "to_str"
]


def from_str(s):
  try:
    return sum(
      int(x) * (60 ** i)
      for i, x in enumerate(reversed(s.split(":")))
    )
  except Exception as e:
    raise ValueError("invalid time '" + s + "'") from e

def to_str(s):
  return time.strftime(
    "%H:%M:%S" if s >= 3600 else "%M:%S",
    time.gmtime(s)
  )


def to_mins(s):
  return s / 60
