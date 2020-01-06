import ast
import astor
import os.path
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

def main(module, filepath, argv=None):
  fsInterface = FsInterface()
  dbInterface = DbInterface()

  sourceCode = fsInterface.readFileSourceCode(filepath)
  tree = ast.parse(sourceCode)
  moduleAlias = findModuleAlias(tree, module)

  if moduleAlias is None:
    return

  rules = dbInterface.findRulesByModule(module)

  for rule in rules:
    applyRule(rule, moduleAlias, tree)

  convertedCode = astor.to_source(tree)
  fsInterface.saveConvertedCode(filepath, convertedCode)

if __name__ == '__main__':
  main()
