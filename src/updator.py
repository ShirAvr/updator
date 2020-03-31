import ast
import astor
# import argparse
import click
import os.path
import os
from tabulate import tabulate
import src.astPatternBuilder as patternBuilder
from src.dbInterface import DbInterface
from src.fsInterface import FsInterface
from src.astPatternConverter import AstPatternConverter

__version__ = '0.1'

def findModuleAlias(tree, moduleName):
  class AliasFinder(ast.NodeVisitor):

    def __init__(self, moduleName):
      super(AliasFinder, self).__init__()
      self.moduleName = moduleName;
      self.aliasModuleName = None;

    def visit_alias(self, node):
      if (node.name is self.moduleName and node.asname is not None):
        self.aliasModuleName = node.asname
      elif (node.name is self.moduleName and node.asname is None):
        self.aliasModuleName = node.name

    def get_found_alias(self):
      return self.aliasModuleName

  class ImportFinder(ast.NodeVisitor):
    def __init__(self, moduleName):
      super(ImportFinder, self).__init__()
      self.moduleName = moduleName;
      self.aliasFinderClass = AliasFinder(self.moduleName)

    def visit_Import(self, node):
      self.aliasFinderClass.visit(node)

    def get_found_alias(self):
      return self.aliasFinderClass.get_found_alias()

  aliasFinderClass = ImportFinder(moduleName)
  aliasFinderClass.visit(tree)
  return aliasFinderClass.get_found_alias()

def applyRule(rule, module, tree):
  patternToSearch = rule["patternToSearch"]
  patternToReplace = rule["patternToReplace"]
  patternVars = {}

  patternToSearch = patternBuilder.preparePattern(patternToSearch, module)
  patternToReplace = patternBuilder.preparePattern(patternToReplace, module)

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

# def main(module, filepath, argv=None):

@click.group()

def main():
  """Automatically upgrade your code"""

@main.command()
@click.argument('lib', metavar="lib", type=click.STRING)
@click.argument('path', metavar="path", type=click.Path(exists=True))

def run(lib, path):
  """execute updator to apply the upgrade"""
  fsInterface = FsInterface()
  dbInterface = DbInterface()

  sourceCode = fsInterface.readFileSourceCode(path)
  tree = ast.parse(sourceCode)
  moduleAlias = findModuleAlias(tree, lib)

  if moduleAlias is None:
    return

  rules = dbInterface.findRulesByModule(lib)

  for rule in rules:
    applyRule(rule, moduleAlias, tree)

  convertedCode = astor.to_source(tree)
  fsInterface.saveConvertedCode(args.path, convertedCode)

  print("finish")

@main.command()
def show_libs():
  """show list of libraries"""
  dbInterface = DbInterface()
  libs = dbInterface.getLibs()
  libs = map(lambda l: [l["_id"], l["count"]], libs)
  print(tabulate(list(libs), headers=["library", "rules count"]))

@main.command()
@click.argument('lib', metavar="lib", type=click.STRING)
def show_rules(lib):
  """show list of rules of a certain library"""
  dbInterface = DbInterface()
  print("all libs")

@main.command()
@click.argument('lib', metavar="lib", type=click.STRING)
@click.argument('ruleNum', metavar="ruleNum", type=click.INT)
def filter_rule(lib, ruleNum):
  """filter rule of a certain library"""

  dbInterface = DbInterface()
  print("all libs")

@main.command()
@click.argument('lib', metavar="lib", type=click.STRING)
@click.argument('patternToSearch', metavar="patternToSearch", type=click.STRING)
@click.argument('patternToReplace', metavar="patternToReplace", type=click.STRING)
def add_rule(lib, patternToSearch, patternToReplace):
  """add rule to a certain library"""
  dbInterface = DbInterface()
  print("all libs")

if __name__ == '__main__':
  main()
