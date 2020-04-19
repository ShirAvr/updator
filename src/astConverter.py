import ast
import copy
import src.astPatternBuilder as patternBuilder
from src.astcompare import is_ast_like 


class AstConverter:
  """Scans Python code for AST nodes matching pattern.
  :param ast.AST pattern: The node pattern to search for
  """
  def __init__(self, rule, patternVars={}, assignRule=False):
    self.patternToSearch = rule.get("patternToSearch")
    self.patternToReplace = rule.get("patternToReplace")
    self.variables = patternVars

    if assignRule:
      self.assignRule = True
      self.assignmentPattern = rule["assignmentPattern"]

  def scan_ast(self, tree):
    """Walk an AST and replace nodes matching pattern.
    :param ast.AST tree: The AST in which to search
    """
    patternSelf = self
    patternToSearch = self.patternToSearch
    patternToReplace = self.patternToReplace
    nodetype = type(patternToSearch)

    # print("patternToSearch: "+ ast.dump(patternToSearch))

    class convertTree(ast.NodeTransformer):
      def visit(self, node):
        ast.NodeVisitor.visit(self, node)

        # print("=")
        # print("node: "+ ast.dump(node))
        # print("patternToSearch: "+ ast.dump(patternToSearch))
        # print("=")

        if isinstance(node, nodetype) and is_ast_like(node, patternToSearch, patternSelf.variables):
          # print("found node: " + ast.dump(node))
          if patternToReplace is not None and patternSelf.variables != {}:
            newNode = AstConverter.fillVariables(patternSelf, node, patternToReplace)
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

  def scan_ast_forAssignment(self, tree):
    """Walk an AST and replace nodes matching pattern.
    :param ast.AST tree: The AST in which to search
    """
    patternSelf = self
    patternToSearch = self.patternToSearch
    patternToReplace = self.patternToReplace
    assignmentPattern = self.assignmentPattern
    patternToSearchType = type(patternToSearch)
    assignPatternType = type(assignmentPattern)

    # print("assignmentPattern: "+ ast.dump(assignmentPattern))

    class convertTree(ast.NodeTransformer):
      def visit(self, node):
        ast.NodeVisitor.visit(self, node)

        isinstance(node, assignPatternType) and is_ast_like(node, assignmentPattern, patternSelf.variables, assignment=True)

        if isinstance(node, patternToSearchType) and is_ast_like(node, patternToSearch, patternSelf.variables, assignment=True):
          # print("found node: " + ast.dump(node))
          if patternToReplace is not None and patternSelf.variables != {}:
            newNode = AstConverter.fillVariables(patternSelf, node, patternToReplace)
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
