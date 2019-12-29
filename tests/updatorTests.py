import sys
import unittest
import textwrap
from dbInterface import DbInterface

# sys.path.insert(1, '../updator')
# from updator import execute, main
import updator

fileToConvert = "./tests/codeFileToConvert.py"

class UpdatorTests(unittest.TestCase):
  # def __init__(self, *args):
    # self.dbInterface = MongodbInterface()

  def __init__(self, *args, **kwargs):
    super(UpdatorTests, self).__init__(*args, **kwargs)
    self.dbInterface = DbInterface()
    self.dbInterface.dropRules()

  def setUp(self):
    print(self._testMethodName)

  def insertRules(self, rules):
    self.dbInterface.insertRules(rules)

    # DbInterface().insertRules(rules)

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

  def test_one_rule_rename_function(self):
    rules = [ {
        "moudle": "os",
        "patternToSearch": "remove()",
        "patternToReplace": "delete()"
      },
      {
        "moudle": "os",
        "patternToSearch": "os.path",
        "patternToReplace": "os.full_path"
      },
      {
        "moudle": "math",
        "patternToSearch": "pow($1, $2)",
        "patternToReplace": "pow($2, $1)"
      } 
    ]

    self.insertRules(rules)

    sourceCode = '''
      import os
      os.remove()        
    '''

    expectedConvertedCode = '''
      import os
      os.delete()        
    '''

    self.createCodeFile(sourceCode)
    moudleName = "os"

    # execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    # actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    # expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    # self.assertTrue(actualConvertedCode == expectedConvertedCode)
    updator.main(moudleName, fileToConvert)

