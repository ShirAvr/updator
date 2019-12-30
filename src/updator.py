import ast
from src.dbInterface import DbInterface
from src.fsInterface import FsInterface
from src.astPatternConverter import AstPatternConverter
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
  s = addAliasToPatterns(s, moudleAlias)
  s = replacingWildCardSigns(s)

  pattern = ast.parse(s).body[0]
  if isinstance(pattern, ast.Expr):
    pattern = pattern.value
  if isinstance(pattern, (ast.Attribute, ast.Subscript)):
    del pattern.ctx

  return pattern

def defineWildcard(matchedWildcard):
  variable_num = matchedWildcard.group()[1]
  return WILDCARD_NAME + variable_num

def replacingWildCardSigns(pattern):
  pattern = pattern.replace(MULTIWILDCARD_SIGN, MULTIWILDCARD_NAME)
  pattern = re.sub(r'[$]\d', defineWildcard, pattern)
  return pattern

def prepareReplacingPattern(patternToReplace, moudleAlias):
  if patternToReplace is "":
    return None

  patternToReplace = replacingWildCardSigns(patternToReplace)

  # class AttrLister(ast.NodeVisitor):
  #   def visit_Attribute(self, node):
  #     global attrPattern
  #     attrPattern = node
  #     self.generic_visit(node)

  # class CallLister(ast.NodeVisitor):
  #     def visit_Call(self, node):
  #         global callPattern
  #         callPattern = node
  #         self.generic_visit(node)

  patternToReplace = addAliasToPatterns(patternToReplace, moudleAlias)
  patternToReplace = ast.parse(patternToReplace)
  # AttrLister().visit(patternToReplace)
  return patternToReplace
  # return callPattern
  # return attrPattern

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

def applyRule(rule, moudle, tree):
  patternToSearch = rule["patternToSearch"]
  patternToReplace = rule["patternToReplace"]
  patternVars = {}

  patternToSearch = prepare_pattern(patternToSearch, patternVars, moudle)
  patternToReplace = prepareReplacingPattern(patternToReplace, moudle)
  patternConverter = AstPatternConverter(patternToSearch, patternToReplace, patternVars)

  # print("patternToSearch: " + ast.dump(patternToSearch))
  # print("patternToReplace: " + ast.dump(patternToReplace))

  # print("=========== before ==========")
  # print(ast.dump(tree))
  # print("==============================")
  
  patternConverter.scan_ast(tree)
  
  # print("=========== after: ==========")
  # print(ast.dump(tree))
  # print("============================")

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
    applyRule(rule, moudleAlias, tree)

  convertedCode = astor.to_source(tree)
  fsInterface.saveConvertedCode(filepath, convertedCode)

if __name__ == '__main__':
  main()
