import ast
import copy
import src.astPatternBuilder as patternBuilder
from src.astcompare import is_ast_like 


class AstPatternConverter:
  """Scans Python code for AST nodes matching pattern.
  :param ast.AST pattern: The node pattern to search for
  """
  def __init__(self, pattrenToSearch, patternToReplace, patternVars={}):
    self.pattrenToSearch = pattrenToSearch
    self.patternToReplace = patternToReplace
    self.variables = patternVars

  def scan_ast(self, tree):
    """Walk an AST and replace nodes matching pattern.
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

        # print("====")
        # print("patternToReplace: "+ ast.dump(patternToReplace))
        # print("node: "+ ast.dump(node))
        # print("====")

        if isinstance(node, nodetype) and is_ast_like(node, pattrenToSearch, patternSelf.variables):
          print("found node")
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

    class RetransformPattern(ast.NodeTransformer):
      def visit_Name(self, node):
        if patternSelf.is_wildcard(node):
          return variables[node.id]
        else:
          return node

    patternToReplace = copy.deepcopy(patternToReplace)
    return RetransformPattern().visit(patternToReplace)

  def is_wildcard(self, nodePattern):
    return patternBuilder.is_wildcard(nodePattern)

  def isInvalidNode(self, node):
    return isinstance(node, ast.Expr) and self.isInvalidExpr(node)

  def isInvalidExpr(self, expNode):
    try:
      expNode.value
    except:
      return True

    return False
