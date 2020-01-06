import sys
import unittest
import textwrap
from src.dbInterface import DbInterface
from src.updator import main

fileToConvert = "./tests/codeFileToConvert.py"

class UpdatorTests(unittest.TestCase):
  def __init__(self, *args, **kwargs):
    super(UpdatorTests, self).__init__(*args, **kwargs)
    self.dbInterface = DbInterface()

  def setUp(self):
    print(self._testMethodName)
    self.dbInterface.dropRules()

  def insertRules(self, rules):
    self.dbInterface.insertRules(rules)

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

  def setUpClass():
    print("------------------------")
    print("Updator end-to-end tests")
    print("------------------------")

  def test_apply_one_rule_change_params_positions(self):
    rules = [ {
        "module": "os",
        "patternToSearch": "remove()",
        "patternToReplace": "delete()"
      },
      {
        "module": "os",
        "patternToSearch": "path",
        "patternToReplace": "full_path"
      },
      {
        "module": "math",
        "patternToSearch": "pow($1, $2)",
        "patternToReplace": "pow($2, $1)"
      } 
    ]

    self.insertRules(rules)

    sourceCode = '''
      import math
      import os
      x = 2
      y = 3
      math.pow(x, y)
      os.remove()
    '''

    expectedConvertedCode = '''
      import math
      import os
      x = 2
      y = 3
      math.pow(y, x)
      os.remove()
    '''

    moduleName = "math"
    self.createCodeFile(sourceCode)
    main(moduleName, fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_apply_two_rules_rename_func_and_attr(self):
    rules = [ {
        "module": "os",
        "patternToSearch": "remove()",
        "patternToReplace": "delete()"
      },
      {
        "module": "os",
        "patternToSearch": "path",
        "patternToReplace": "full_path"
      },
      {
        "module": "math",
        "patternToSearch": "pow($1, $2)",
        "patternToReplace": "pow($2, $1)"
      } 
    ]

    self.insertRules(rules)

    sourceCode = '''
      import os
      os.remove()
      a = 1 + 4
      b = 2
      print(os.path)
      c = a + b
    '''

    expectedConvertedCode = '''
      import os
      os.delete()
      a = 1 + 4
      b = 2
      print(os.full_path)
      c = a + b
    '''

    moduleName = "os"
    self.createCodeFile(sourceCode)
    main(moduleName, fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_apply_two_rules_on_the_same_expression(self):
    rules = [ {
        "module": "os",
        "patternToSearch": "remove($all)",
        "patternToReplace": "delete($all)"
      },
      {
        "module": "os",
        "patternToSearch": "path",
        "patternToReplace": "full_path"
      },
      {
        "module": "math",
        "patternToSearch": "pow($1, $2)",
        "patternToReplace": "pow($2, $1)"
      } 
    ]

    self.insertRules(rules)

    sourceCode = '''
      import os
      os.remove(os.path)
      a = 1 + 4
      b = 2
      print(os.path)
      c = a + b
    '''

    expectedConvertedCode = '''
      import os
      os.delete(os.full_path)
      a = 1 + 4
      b = 2
      print(os.full_path)
      c = a + b
    '''

    moduleName = "os"
    self.createCodeFile(sourceCode)
    main(moduleName, fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_execute_with_differents_modules(self):
    rules = [ {
        "module": "os",
        "patternToSearch": "remove($all)",
        "patternToReplace": "delete($all)"
      },
      {
        "module": "os",
        "patternToSearch": "path",
        "patternToReplace": "full_path"
      },
      {
        "module": "math",
        "patternToSearch": "pow($1, $2)",
        "patternToReplace": "pow($2, $1)"
      },
      {
        "module": "tensorflow",
        "patternToSearch": "Variable($1, $2)",
        "patternToReplace": "Variable($1)"
      } 
    ]

    self.insertRules(rules)

    sourceCode = '''
      import os
      import math
      import tensorflow as tf
      os.remove(os.path)
      a = 1 + 4
      b = math.pow(2, a)
      print(os.path)
      c = a + b
      tf.Variable(c, "x")
    '''

    expectedConvertedCode = '''
      import os
      import math
      import tensorflow as tf
      os.delete(os.full_path)
      a = 1 + 4
      b = math.pow(a, 2)
      print(os.full_path)
      c = a + b
      tf.Variable(c)
    '''

    self.createCodeFile(sourceCode)
    main("os", fileToConvert)
    main("math", fileToConvert)
    main("tensorflow", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)

    self.assertTrue(actualConvertedCode == expectedConvertedCode)


