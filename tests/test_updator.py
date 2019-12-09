import ast
# from updator import execute
import sys
import importlib
import unittest

sys.path.insert(1, '../updator')
from updator import execute

moudleName = "sys"
codeMoudleName = None
attrPattern = None
callPattern = None

fileName = "./funcExample.py"
# codeToConvert = import "./pythonCodeExample.py"


# this part of code should move into updator.py! (retrieveMoudleAlias)
# By that we can find the name of the moudle in the source code.
# if they used import.. as - we could figure out the alias of the moudle
class AliasLister(ast.NodeVisitor):
  def visit_alias(self, node):
      global codeMoudleName

      if (node.name is moudleName and node.asname is not None):
      	codeMoudleName = node.asname
      elif (node.name is moudleName and node.asname is None):
      	codeMoudleName = node.name
      self.generic_visit(node)

class FuncLister(ast.NodeVisitor):
  def visit_Import(self, node):
      #print(ast.dump(node))
      #print(node.names[0])
      AliasLister().visit(node)
      self.generic_visit(node)

class AttrLister(ast.NodeVisitor):
  def visit_Attribute(self, node):
      global attrPattern
      attrPattern = node
      self.generic_visit(node)

class CallLister(ast.NodeVisitor):
  def visit_Call(self, node):
      global callPattern
      callPattern = node
      self.generic_visit(node)

fileString = (open(fileName, 'rb')).read()
tree = ast.parse(fileString)

FuncLister().visit(tree)

pattrenToSearch = codeMoudleName + ".exc_info(??)"
pattrenToReplace = codeMoudleName + ".execute_info(v1)"
# pattrenToReplace = ast.parse(pattrenToReplace)
# CallLister().visit(pattrenToReplace)

# print("patternToReplace: "+ ast.dump(callPattern))

# execute(pattrenToSearch, callPattern, fileName)

class UpdatorTests(unittest.TestCase):
  def __init__(self, *args, **kwargs):
    super(UpdatorTests, self).__init__(*args, **kwargs)
    global codeMoudleName
    self.codeMoudleName = codeMoudleName;

  def test_convert_function_name(self):
    pattrenToSearch = self.codeMoudleName + ".exc_info(??)"
    pattrenToReplace = self.codeMoudleName + ".execute_info(v1)"
    execute(pattrenToSearch, pattrenToReplace, fileName)

    self.assertTrue(True)

  def test_convert_function_name_with_one_arg(self):
    self.assertTrue(True)

  def test_convert_function_name_with_args(self):
    self.assertTrue(True)

  def test_convert_attribute_name(self):
    self.assertTrue(True)



