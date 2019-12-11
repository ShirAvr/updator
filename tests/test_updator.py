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


fileString = (open(fileName, 'rb')).read()
tree = ast.parse(fileString)

class AttrLister(ast.NodeVisitor):
  def visit_Attribute(self, node):
      global attrPattern
      attrPattern = node
      self.generic_visit(node)

class CallLister(ast.NodeVisitor):
  def __init__(self, ):
    # super(UpdatorTests, self).__init__(*args, **kwargs)
    super(CallLister, self).__init__()

  def visit_Call(self, node):
      global callPattern
      callPattern = node
      self.generic_visit(node)


pattrenToSearch = "exc_info(??)"
pattrenToReplace = "execute_info(v1)"

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
    pattrenToSearch = "exc_info(??)"
    pattrenToReplace = "execute_info(v1)"
    execute(pattrenToSearch, pattrenToReplace, fileName, moudleName)

    self.assertTrue(True)

  def test_convert_function_name_with_one_arg(self):
    self.assertTrue(True)

  def test_convert_function_name_with_args(self):
    self.assertTrue(True)

  def test_convert_attribute_name(self):
    self.assertTrue(True)



