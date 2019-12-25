import ast
# from updator import execute
import sys
import importlib
import unittest
import textwrap

# sys.path.insert(1, '../updator')
from updator import execute

moudleName = "sys"
codeMoudleName = None
attrPattern = None
callPattern = None

fileName = "./funcExample.py"
fileToConvert = "./tests/codeFileToConvert.py"


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

class RenameFunctionTests(unittest.TestCase):
  def __init__(self, *args, **kwargs):
    super(RenameFunctionTests, self).__init__(*args, **kwargs)
    global codeMoudleName
    self.codeMoudleName = codeMoudleName;

  def setUp(self):
    print(self._testMethodName)

  def createCodeFile(self, codeText):
    with open(fileToConvert, 'w') as f:
      f.write(textwrap.dedent(codeText))
      f.close()

  def readCodeFile(self):
    with open(fileToConvert, 'r') as f:
      codeContent = f.read()
      f.close()

      return codeContent

  def dropWhitespace(self, str):
    return ''.join(str.split())

  def test_rename_function_without_params(self):
    sourceCode = '''\
      import sys as s
      s.exc_info()        
    '''

    expectedConvertedCode = '''
      import sys as s
      s.execute_info()        
    '''

    self.createCodeFile(sourceCode)
    pattrenToSearch = "exc_info()"
    pattrenToReplace = "execute_info()"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_with_destructure_each_function_params_to_wildcard(self):
    sourceCode = '''\
      import sys as s
      s.exc_info('shir', 'binyamin')        
    '''

    expectedConvertedCode = '''
      import sys as s
      s.execute_info('shir', 'binyamin')        
    '''

    self.createCodeFile(sourceCode)
    pattrenToSearch = "exc_info($1, $2)"
    pattrenToReplace = "execute_info($1, $2)"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_with_destructure_all_params_to_wildcard(self):
    sourceCode = '''\
      import sys as s
      s.exc_info('shir', 'binyamin')        
    '''

    expectedConvertedCode = '''
      import sys as s
      s.execute_info('shir', 'binyamin')        
    '''

    self.createCodeFile(sourceCode)
    pattrenToSearch = "exc_info($all)"
    pattrenToReplace = "execute_info($all)"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_change_between_params_order(self):
    sourceCode = '''\
      import sys as s
      s.exc_info('shir', 'binyamin')        
    '''

    expectedConvertedCode = '''
      import sys as s
      s.execute_info('binyamin', 'shir')        
    '''

    self.createCodeFile(sourceCode)
    pattrenToSearch = "exc_info($1, $2)"
    pattrenToReplace = "execute_info($2, $1)"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  # TODO: add cases of combined $n + $all

  # def test_convert_function_name(self):
  #   pattrenToSearch = "exc_info($1, $2)"
  #   pattrenToReplace = "execute_info($1, $2)"
  #   execute(pattrenToSearch, pattrenToReplace, fileName, moudleName)

  #   self.assertTrue(True)

  # def test_convert_function_name(self):
  #   pattrenToSearch = "exc_info($1, $2)"
  #   pattrenToReplace = "execute_info($2, $1)"
  #   execute(pattrenToSearch, pattrenToReplace, fileName, moudleName)

  #   self.assertTrue(True)

  # def test_convert_function_name(self):
  #   pattrenToSearch = "exc_info($all)"
  #   pattrenToReplace = "execute_info($all)"
  #   execute(pattrenToSearch, pattrenToReplace, fileName, moudleName)

  #   self.assertTrue(True)



  # def test_convert_function_name_with_one_arg(self):
  #   self.assertTrue(True)

  # def test_convert_function_name_with_args(self):
  #   self.assertTrue(True)

  # def test_convert_attribute_name(self):
  #   self.assertTrue(True)



