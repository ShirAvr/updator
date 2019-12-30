from src.astcompare import is_ast_like 
import ast
import astor
import os.path
import sys
import tokenize
import warnings
import re
import copy

WILDCARD_NAME = "__updator_wildcard"
MULTIWILDCARD_NAME = "__updator_multiwildcard"

# WILDCARD_SIGN = "$"
MULTIWILDCARD_SIGN = "$all"

class AstPatternConverter(object):
  """Scans Python code for AST nodes matching pattern.

  :param ast.AST pattern: The node pattern to search for
  """
  def __init__(self, pattrenToSearch, patternToReplace, patternVars={}):
      self.pattrenToSearch = pattrenToSearch
      self.patternToReplace = patternToReplace
      self.variables = patternVars

  def scan_ast(self, tree):
    """Walk an AST and yield nodes matching pattern.
    :param ast.AST tree: The AST in which to search
    """
    patternSelf = self
    pattrenToSearch = self.pattrenToSearch
    patternToReplace = self.patternToReplace
    nodetype = type(pattrenToSearch)

    # print("patternToReplace: "+ ast.dump(patternToReplace))

    class convertTree(ast.NodeTransformer):
      def visit(self, node):
        ast.NodeVisitor.visit(self, node)

        if isinstance(node, nodetype) and is_ast_like(node, pattrenToSearch, patternSelf.variables):
          # print("found node: " + ast.dump(node))
          if patternToReplace is not None and patternSelf.variables != {}:
            newNode = AstPatternConverter.fillVariables(patternSelf, node, patternToReplace)
            newNode = ast.copy_location(newNode, node) # not sure it's needed
          else:
            newNode = patternToReplace

          # print("new node: " + ast.dump(newNode))

          return newNode
        elif patternSelf.isInvalidNode(node):
          return None
        else:
          return node

    convertTree().visit(tree)

  def fillVariables(self, foundNode, patternToReplace):
      variables = self.variables
      patternSelf = self

      if variables == {}:
        return patternToReplace

      class retransformPattern(ast.NodeTransformer):
        def visit_Name(self, node):
          if patternSelf.is_wildcard(node):
            return variables[node.id]
          else:
            return node

      patternToReplace = copy.deepcopy(patternToReplace)
      return retransformPattern().visit(patternToReplace)

  def is_wildcard(self, node):
    is_wildcard = node.id[:-1] == WILDCARD_NAME
    is_multi_wildcard = node.id == MULTIWILDCARD_NAME
    return is_wildcard or is_multi_wildcard

  def scan_file(self, file):
    """Parse a file and yield AST nodes matching pattern.

    :param file: Path to a Python file, or a readable file object
    """
    if isinstance(file, str):
      with open(file, 'rb') as f:
        tree = ast.parse(f.read())
    else:
      tree = ast.parse(file.read())
    yield from self.scan_ast(tree)

  def filter_subdirs(self, dirnames):
      dirnames[:] = [d for d in dirnames if d != 'build']

  def scan_directory(self, directory):
      """Walk files in a directory, yielding (filename, node) pairs matching
      pattern.

      :param str directory: Path to a directory to search

      Only files with a ``.py`` or ``.pyw`` extension will be scanned.
      """
      for dirpath, dirnames, filenames in os.walk(directory):
          self.filter_subdirs(dirnames)

          for filename in filenames:
              if filename.endswith(('.py', '.pyw')):
                  filepath = os.path.join(dirpath, filename)
                  try:
                      for match in self.scan_file(filepath):
                          yield filepath, match
                  except SyntaxError as e:
                      warnings.warn("Failed to parse {}:\n{}".format(filepath, e))

  def isInvalidNode(self, node):
    return isinstance(node, ast.Expr) and self.isInvalidExpr(node)

  def isInvalidExpr(self, expNode):
    try:
      expNode.value
    except:
      return True

    return False
