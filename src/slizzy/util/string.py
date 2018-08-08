import ast
import re


__all__ = [
  "literal",
  "normalize_spaces",
  "read_int",
  "read_float"
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

