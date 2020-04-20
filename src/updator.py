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
from src.astConverter import AstConverter

__version__ = '0.1'

def findModuleAlias(tree, moduleName):
  class AliasFinder(ast.NodeVisitor):

    def __init__(self, moduleName):
      super(AliasFinder, self).__init__()
      self.moduleName = moduleName
      self.aliasModuleName = None

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
  if rule.get("isAssignmentRule"):
    applyAssignmentRule(rule, module, tree, shouldBuild=False)
  else:
    if rule.get("applyToAssignment"):
      applyAssignmentRule(rule, module, tree, shouldBuild=True)

    patternVars = {}
    
    rule = patternBuilder.prepareRule(rule, module)
    astConverter = AstConverter(rule, patternVars)

    # print("patternToSearch: " + ast.dump(patternToSearch))
    # print("patternToReplace: " + ast.dump(patternToReplace))

    # print("=========== before ==========")
    # print(ast.dump(tree))
    # print("==============================")
    
    astConverter.scan_ast(tree)

# def applyRule(rule, module, tree):
#   if rule.get("applyToAssignment"):
#     applyAssignmentRule(rule, module, tree)

#   patternVars = {}
  
#   rule = patternBuilder.prepareRule(rule, module)
#   astConverter = AstConverter(rule, patternVars)

#   # print("patternToSearch: " + ast.dump(patternToSearch))
#   # print("patternToReplace: " + ast.dump(patternToReplace))

#   # print("=========== before ==========")
#   # print(ast.dump(tree))
#   # print("==============================")
  
#   astConverter.scan_ast(tree)
  
#   # print("=========== after: ==========")
#   # print(ast.dump(tree))
#   # print("============================")

# def cli(module, filepath, argv=None):

def applyAssignmentRule(rule,  module, tree, shouldBuild):
  assignmentRule = patternBuilder.createAssignmentRule(rule, module, shouldBuild)
  patternVars = {}

  astConverter = AstConverter(assignmentRule, patternVars, assignRule=True)
  astConverter.scan_ast_forAssignment(tree)

def showRules(dbInterface, lib):
  rules = dbInterface.findAllRulesByLib(lib)
  rules = list(map(lambda r: [r["patternToSearch"], r["patternToReplace"], r["active"]], rules))

  if rules == []:
    print("library '" + lib + "' does not exists.")
  else:
    print("Rules for '" + lib + "' library: \n")
    print(tabulate(rules, headers=["id", "patternToSearch", "patternToReplace", "active"], showindex="always"))

  return rules


@click.group()

def main():
  """Automatically upgrade your code"""

@main.command()
@click.argument('lib', metavar="lib", type=click.STRING)
# @click.argument('path', metavar="path", type=click.Path(exists=True))
@click.argument('path', metavar="path", type=click.STRING)

# def main(module, filepath, argv=None):  
def run(lib, path):
  """execute updator to apply the upgrade"""
  fsInterface = FsInterface()
  dbInterface = DbInterface()

  sourceCode = fsInterface.readFileSourceCode(path)
  tree = ast.parse(sourceCode)
  moduleAlias = findModuleAlias(tree, lib)

  if moduleAlias is None:
    return

  rules = dbInterface.findRulesByLib(lib)

  for rule in rules:
    applyRule(rule, moduleAlias, tree)
  
  # print("=========== after: ==========")
  # print(ast.dump(tree))
  # print("============================")
  convertedCode = astor.to_source(tree)
  fsInterface.saveConvertedCode(path, convertedCode)

  # print("finish")

@main.command()
def show_libs():
  """show list of libraries"""
  dbInterface = DbInterface()
  libs = dbInterface.findLibs()
  libs = map(lambda l: [l["_id"], l["count"]], libs)
  print(tabulate(list(libs), headers=["library", "rules count"]))

@main.command()
@click.argument('lib', metavar="lib", type=click.STRING)
def show_rules(lib):
  """show list of rules of a certain library"""
  dbInterface = DbInterface()
  showRules(dbInterface, lib)

@main.command()
@click.argument('lib', metavar="lib", type=click.STRING)
def deactivate_rule(lib):
  """deactivate rule of a certain library"""
  dbInterface = DbInterface()
  rules = showRules(dbInterface, lib)
  if rules != []:
    choices= [str(i) for i in range(len(rules))]
    id = click.prompt("Chose rule id to deactivate", type=click.Choice(choices), confirmation_prompt=True)
    dbInterface.deactivateRule({"module": lib, "patternToSearch": rules[int(id)][0]})
    print("\nDeactivate rule id (" + id + ") successfully.")
    showRules(dbInterface, lib)

@main.command()
@click.argument('lib', metavar="lib", type=click.STRING)
def reactivate_rule(lib):
  """reactivate rule of a certain library"""
  dbInterface = DbInterface()
  rules = showRules(dbInterface, lib)
  if rules != []:
    choices= [str(i) for i in range(len(rules))]
    id = click.prompt("Chose rule id to reactivate", type=click.Choice(choices), confirmation_prompt=True)
    dbInterface.reactivateRule({"module": lib, "patternToSearch": rules[int(id)][0]})
    print("\nReactivate rule id (" + id + ") successfully.")
    showRules(dbInterface, lib)

@main.command()
@click.argument('lib', metavar="lib", type=click.STRING)
def add_rule(lib):
  """add rule to a certain library"""
  patternToSearch = click.prompt("Enter pattern to search", type=click.STRING)
  patternToReplace = click.prompt("Enter pattern to replace", type=click.STRING)
  click.confirm("Do you confirm?", abort=True)

  try:
    ast.parse(patternToSearch)
    ast.parse(patternToReplace)
  except:
    print("Given patterns are not valid.")
  else:
    DbInterface().insertRule({
      "module": lib,
      "patternToSearch": patternToSearch,
      "patternToReplace": patternToReplace
    })
    print("Inserted given rule successfully.")

if __name__ == '__main__':
  main()
