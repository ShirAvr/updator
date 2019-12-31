import ast
import astor
import os.path
import src.astPatternBuilder as patternBuilder
from src.dbInterface import DbInterface
from src.fsInterface import FsInterface
from src.astPatternConverter import AstPatternConverter

__version__ = '0.1'

def findMoudleAlias(tree, moudleName):
  class AliasFinder(ast.NodeVisitor):

    def __init__(self, moudleName):
      super(AliasFinder, self).__init__()
      self.moudleName = moudleName;
      self.aliasMoudleName = None;

    def visit_alias(self, node):
        if (node.name is self.moudleName and node.asname is not None):
          self.aliasMoudleName = node.asname
        elif (node.name is self.moudleName and node.asname is None):
          self.aliasMoudleName = node.name

    def get_found_alias(self):
      return self.aliasMoudleName

  class ImportFinder(ast.NodeVisitor):
    def __init__(self, moudleName):
      super(ImportFinder, self).__init__()
      self.moudleName = moudleName;
      self.aliasFinderClass = AliasFinder(self.moudleName)

    def visit_Import(self, node):
      self.aliasFinderClass.visit(node)

    def get_found_alias(self):
      return self.aliasFinderClass.get_found_alias()

  aliasFinderClass = ImportFinder(moudleName)
  aliasFinderClass.visit(tree)
  return aliasFinderClass.get_found_alias()

def applyRule(rule, moudle, tree):
  patternToSearch = rule["patternToSearch"]
  patternToReplace = rule["patternToReplace"]
  patternVars = {}

  patternToSearch = patternBuilder.preparePattern(patternToSearch, moudle)
  patternToReplace = patternBuilder.preparePattern(patternToReplace, moudle)

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
