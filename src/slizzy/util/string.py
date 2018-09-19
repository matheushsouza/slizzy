import ast
import re
from fuzzywuzzy import fuzz


__all__ = [
  "literal",
  "normalize_spaces",
  "read_int",
  "read_float",
  "fuzz_match"
]


def literal(string):
  return ast.literal_eval(string.strip())


def normalize_spaces(string):
  return re.sub(r" +", " ", string).strip()


def read_int(string):
  try:
    return int(next(re.finditer(r"\d+", string)).group())
  except StopIteration:
    raise ValueError("no integer in string") from None


def read_float(string):
  try:
    return float(next(re.finditer(r"\d+\.\d+", string)).group())
  except StopIteration:
    raise ValueError("no float in string") from None


def read_number(string):
  try:
    return read_float(string)
  except:
    pass

  try:
    return read_int(string)
  except:
    raise ValueError("no number in string") from None


def fuzz_match(s1, s2):
  return fuzz.ratio(s1.lower(), s2.lower())
