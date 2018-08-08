def partition(pred, iterable):
  trues, falses = [], []
  
  for item in iterable:
    (trues if pred(item) else falses).append(item)
  
  return trues, falses
