import ast
import astcompare
# from fs import ASTPatternConverter
# import a
from dbInterface import DbInterface
from fsInterface import FsInterface
from astPatternConverter import AstPatternConverter
from astcompare import assert_ast_like
import astor
import os.path
import sys
import tokenize
import warnings
import re
import copy
from functools import partial

__version__ = '0.1'

WILDCARD_NAME = "__updator_wildcard"
MULTIWILDCARD_NAME = "__updator_multiwildcard"

# WILDCARD_SIGN = "$"
MULTIWILDCARD_SIGN = "$all"

def prepare_pattern(s, _vars=[], moudleAlias=""):
    """Turn a string pattern into an AST pattern

    This parses the string to an AST, and generalises it a bit for sensible
    matching. ``?`` is treated as a wildcard that matches anything. Names in
    the pattern will match names or attribute access (i.e. ``foo`` will match
    ``bar.foo`` in files).
    """
    s = addAliasToPatterns(s, moudleAlias)
    s = replacingWildCardSigns(s)

    pattern = ast.parse(s).body[0]
    if isinstance(pattern, ast.Expr):
        pattern = pattern.value
    if isinstance(pattern, (ast.Attribute, ast.Subscript)):
        # If the root of the pattern is like a.b or a[b], we want to match it
        # regardless of context: `a.b=2` and `del a.b` should match as well as
        # `c = a.b`
        del pattern.ctx
    # return TemplatePruner(_vars=_vars).visit(pattern)
    return pattern

def defineWildcard(matchedWildcard):
  variable_num = matchedWildcard.group()[1]
  return WILDCARD_NAME + variable_num

def replacingWildCardSigns(pattern):
  pattern = pattern.replace(MULTIWILDCARD_SIGN, MULTIWILDCARD_NAME)
  pattern = re.sub(r'[$]\d', defineWildcard, pattern)
  return pattern

def prepareReplacingPattern(pattrenToReplace, moudleAlias):
  if pattrenToReplace is "":
    return None

  pattrenToReplace = replacingWildCardSigns(pattrenToReplace)

  # class AttrLister(ast.NodeVisitor):
  #     def visit_Attribute(self, node):
  #         global attrPattern
  #         attrPattern = node
  #         self.generic_visit(node)

  # class CallLister(ast.NodeVisitor):
  #     def visit_Call(self, node):
  #         global callPattern
  #         callPattern = node
  #         self.generic_visit(node)

  pattrenToReplace = addAliasToPatterns(pattrenToReplace, moudleAlias)
  pattrenToReplace = ast.parse(pattrenToReplace)
  # CallLister().visit(pattrenToReplace)
  return pattrenToReplace
  # return callPattern

def addAliasToPatterns(pattern, moudleAlias):
    return moudleAlias + "." + pattern;

def findMoudleAlias(tree, givenMoudleName):
  class AliasFinder(ast.NodeVisitor):

    def __init__(self, givenMoudleName):
      super(AliasFinder, self).__init__()
      self.givenMoudleName = givenMoudleName;
      self.aliasMoudleName = None;

    def visit_alias(self, node):
        if (node.name is self.givenMoudleName and node.asname is not None):
          self.aliasMoudleName = node.asname
        elif (node.name is self.givenMoudleName and node.asname is None):
          self.aliasMoudleName = node.name

    def get_found_alias(self):
      return self.aliasMoudleName

  class ImportFinder(ast.NodeVisitor):
    def __init__(self, givenMoudleName):
      super(ImportFinder, self).__init__()
      self.givenMoudleName = givenMoudleName;
      self.aliasFinderClass = AliasFinder(self.givenMoudleName)

    def visit_Import(self, node):
      self.aliasFinderClass.visit(node)

    def get_found_alias(self):
      return self.aliasFinderClass.get_found_alias()

  aliasFinderClass = ImportFinder(givenMoudleName)
  aliasFinderClass.visit(tree)
  return aliasFinderClass.get_found_alias()

# execute = applyRule
def execute(pattrenToSearch, pattrenToReplace, filepath, givenMoudleName):
  filesInterface = FsInterface()

  sourceCode = filesInterface.readFileSourceCode(filepath)
  tree = ast.parse(sourceCode)
  moudleAlias = findMoudleAlias(tree, givenMoudleName)

  if moudleAlias is None:
    return

  patternVars = {}

  pattrenToSearch = prepare_pattern(pattrenToSearch, patternVars, moudleAlias)
  pattrenToReplace = prepareReplacingPattern(pattrenToReplace, moudleAlias)
  patternConverter = AstPatternConverter(pattrenToSearch, pattrenToReplace, patternVars)

  # print("pattrenToSearch: " + ast.dump(pattrenToSearch))

  # print("=========== before ==========")
  # print(ast.dump(tree))
  # print("==============================")
  
  patternConverter.scan_ast(tree)
  
  # print("=========== after: ==========")
  # print(ast.dump(tree))
  # print("============================")

  convertedCode = astor.to_source(tree)
  filesInterface.saveConvertedCode(filepath, convertedCode)

# execute = applyRule
def applyRule(rule, moudle, filepath):
  # moudleName = rule.moudle
  pattrenToSearch = rule.pattrenToSearch
  pattrenToReplace = rule.pattrenToReplace

  # if moudleAlias is None:
  #   return

  patternVars = {}

  pattrenToSearch = prepare_pattern(pattrenToSearch, patternVars, moudle)
  pattrenToReplace = prepareReplacingPattern(pattrenToReplace, moudle)
  patternConverter = AstPatternConverter(pattrenToSearch, pattrenToReplace, patternVars)

  # print("pattrenToSearch: " + ast.dump(pattrenToSearch))

  # print("=========== before ==========")
  # print(ast.dump(tree))
  # print("==============================")
  
  patternConverter.scan_ast(tree)
  
  # print("=========== after: ==========")
  # print(ast.dump(tree))
  # print("============================")

  convertedCode = astor.to_source(tree)
  filesInterface.saveConvertedCode(filepath, convertedCode)

def main(moudle, filepath, argv=None):
  fsInterface = FsInterface()
  dbInterface = DbInterface()

  sourceCode = fsInterface.readFileSourceCode(filepath)
  tree = ast.parse(sourceCode)
  moudleAlias = findMoudleAlias(tree, moudle)

  if moudleAlias is None:
    return

  rules = dbInterface.findRulesByMoudle(moudle)
  for rule in rules:
    print(rule)


if __name__ == '__main__':
  main()
