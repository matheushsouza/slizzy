import re

from .util import types
from .util import string


@types.auto_str
class Track:
  def __init__(self, title, duration = None):
    self.title = title
    
    slash = title.split("-")
    paren = slash[1].split("(")
    self.artists = string.normalize_spaces(slash[0])
    self.name    = paren[0].strip()
    self.suffix  = paren[1].strip()[:-1] if len(paren) > 1 else None
    
    self.query_string = string.normalize_spaces(
      " ".join([
        re.sub(r"ft\.?|&|vs\.?|,", "", self.artists),
        self.name,
        re.sub(r"ft\.?|&|vs\.?|,", "", self.suffix or ""),
      ])
    ).lower()
    
    self.duration = duration
