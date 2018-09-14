class frange:
  """A frange is a range delimited by two floating point values.
  It is not an enumerator as the standard range."""
  def __init__(self, lower, upper):
    if lower > upper:
      raise ValueError("frage: lower bigger than upper")
    
    self.lower = lower
    self.upper = upper
    

  def __contains__(self, number):
    return self.lower <= number and number <= self.upper
