import ast
import operator as op


__all__ = [
  "eval"
]


# supported operators
operators = {
  ast.Add    : op.add,
  ast.Sub    : op.sub,
  ast.Mult   : op.mul,
  ast.Div    : op.truediv,
  ast.Mod    : op.mod,
  ast.Pow    : op.pow,
  ast.USub   : op.neg
}


def eval(expr):
  return __eval(ast.parse(expr.strip(), mode = "eval").body)


def __eval(node):
  if isinstance(node, ast.Num):
    return node.n
  
  if isinstance(node, ast.BinOp):
    return operators[type(node.op)](__eval(node.left), __eval(node.right))
  
  if isinstance(node, ast.UnaryOp):
    return operators[type(node.op)](__eval(node.operand))
  
  raise TypeError(node)
