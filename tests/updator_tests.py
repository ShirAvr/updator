import sys
import unittest
import textwrap

# sys.path.insert(1, '../updator')
from updator import execute

fileToConvert = "./tests/codeFileToConvert.py"

class UpdatorTests(unittest.TestCase):
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


class UpdatorGenericTests(UpdatorTests):
  def setUpClass():
    print("---------------------")
    print("Updator genric tests")
    print("---------------------")

  def test_moudle_name_unused_in_source_code(self):
    sourceCode = '''
      import math
      x = 2
      y = 3
      math.pow(x, y)     
    '''

    expectedConvertedCode = sourceCode

    self.createCodeFile(sourceCode)
    moudleName = "sys"
    pattrenToSearch = "pow($all)"
    pattrenToReplace = "pow2($all)"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_moudle_name_with_alias(self):
    sourceCode = '''
      import math as m
      x = 2
      y = 3
      m.pow(x, y)     
    '''

    expectedConvertedCode = '''
      import math as m
      x = 2
      y = 3
      m.pow2(x, y)     
    '''

    self.createCodeFile(sourceCode)
    moudleName = "math"
    pattrenToSearch = "pow($all)"
    pattrenToReplace = "pow2($all)"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

# # consider TODO: add a functionTests params where all tests related to function
# # signature will be related. RenameFunctionTests and ReplaceFuncParamsTests will
# # inherent from functionTests, and test as 'pattern should not be found' 
# # will be defined in the new class
class ChangeFunctionSignatureTests(UpdatorTests):
  def setUpClass():
    print("-------------------------------")
    print("Change function signature tests")
    print("-------------------------------")

  def test_rename_function_without_params(self):
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
    pattrenToSearch = "remove()"
    pattrenToReplace = "delete()"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_rename_function_destructure_each_function_params_to_wildcard(self):
    sourceCode = '''
      import os
      os.remove('shir', 'binyamin')        
    '''

    expectedConvertedCode = '''
      import os
      os.delete('shir', 'binyamin')        
    '''

    self.createCodeFile(sourceCode)
    moudleName = "os"
    pattrenToSearch = "remove($1, $2)"
    pattrenToReplace = "delete($1, $2)"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_rename_function_destructure_all_params_to_wildcard(self):
    sourceCode = '''
      import os as s
      s.remove('shir', 'binyamin')        
    '''

    expectedConvertedCode = '''
      import os as s
      s.delete('shir', 'binyamin')        
    '''

    self.createCodeFile(sourceCode)
    moudleName = "os"
    pattrenToSearch = "remove($all)"
    pattrenToReplace = "delete($all)"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_rename_function_and_change_params_order(self):
    sourceCode = '''
      import os as s
      s.remove('shir', 'binyamin')        
    '''

    expectedConvertedCode = '''
      import os as s
      s.delete('binyamin', 'shir')        
    '''

    self.createCodeFile(sourceCode)
    moudleName = "os"
    pattrenToSearch = "remove($1, $2)"
    pattrenToReplace = "delete($2, $1)"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_remove_function_without_params(self):
    sourceCode = '''
      import os as s
      s.remove()
      a = 1 + 2
    '''

    expectedConvertedCode = '''
      import os as s
      a = 1 + 2
    '''

    self.createCodeFile(sourceCode)
    moudleName = "os"
    pattrenToSearch = "remove()"
    pattrenToReplace = ""
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_remove_function_with_params(self):
    sourceCode = '''
      import os
      os.remove("shir")
      b = 1     
    '''

    expectedConvertedCode = '''
      import os
      b = 1
    '''

    self.createCodeFile(sourceCode)
    moudleName = "os"
    pattrenToSearch = "remove($all)"
    pattrenToReplace = ""
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_pattern_to_search_should_not_be_found_case_pattern_without_params(self):
    sourceCode = '''
      import math
      x = 2
      y = 3
      math.pow(x, y)     
    '''

    expectedConvertedCode = sourceCode

    self.createCodeFile(sourceCode)
    moudleName = "math"
    pattrenToSearch = "pow()"
    pattrenToReplace = "pow()"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_pattern_to_search_should_not_be_found_case_pattern_with_too_many_params(self):
    sourceCode = '''
      import math
      x = 2
      y = 3
      math.pow(x, y)     
    '''

    expectedConvertedCode = sourceCode

    self.createCodeFile(sourceCode)
    moudleName = "math"
    pattrenToSearch = "pow($1, $2, $3)"
    pattrenToReplace = "pow()"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_pattern_to_search_should_not_be_found_case_pattern_has_not_enough_params(self):
    sourceCode = '''
      import math
      x = 2
      y = 3
      math.pow(x, y)     
    '''

    expectedConvertedCode = sourceCode

    self.createCodeFile(sourceCode)
    moudleName = "math"
    pattrenToSearch = "pow($1)"
    pattrenToReplace = "pow()"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_multiwildcard_should_match_func_without_params(self):
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
    pattrenToSearch = "remove($all)"
    pattrenToReplace = "delete($all)"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_apply_rule_rename_function_without_params_inside_rule(self):
    sourceCode = '''
      import os
      os.remove(os.remove())
    '''

    expectedConvertedCode = '''
      import os
      os.delete(os.delete())
    '''

    self.createCodeFile(sourceCode)
    moudleName = "os"
    pattrenToSearch = "remove($all)"
    pattrenToReplace = "delete($all)"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_apply_rule_rename_function_inside_rule_when_inner_func_with_params(self):
    sourceCode = '''
      import os
      os.remove(os.remove('shir', 'binyamin'))
    '''

    expectedConvertedCode = '''
      import os
      os.delete(os.delete('shir', 'binyamin'))
    '''

    self.createCodeFile(sourceCode)
    moudleName = "os"
    pattrenToSearch = "remove($all)"
    pattrenToReplace = "delete($all)"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_apply_rule_rename_function_inside_rule_when_outter_func_with_3_params(self):
    sourceCode = '''
      import os
      os.remove(2, os.remove('shir'), 1)
    '''

    expectedConvertedCode = '''
      import os
      os.delete(2, os.delete('shir'), 1)
    '''

    self.createCodeFile(sourceCode)
    moudleName = "os"
    pattrenToSearch = "remove($all)"
    pattrenToReplace = "delete($all)"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_apply_rule_rename_function_inside_rule_when_inner_pattern_exists_twice(self):
    sourceCode = '''
      import os
      os.remove(os.remove('bin'), os.remove('shir'), 1)
    '''

    expectedConvertedCode = '''
      import os
      os.delete(os.delete('bin'), os.delete('shir'), 1)
    '''

    self.createCodeFile(sourceCode)
    moudleName = "os"
    pattrenToSearch = "remove($all)"
    pattrenToReplace = "delete($all)"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_apply_rule_rename_function_inside_rule_inside_rule(self):
    sourceCode = '''
      import os
      os.remove(os.remove(os.remove('shir', 1), 2), 3)
    '''

    expectedConvertedCode = '''
      import os
      os.delete(os.delete(os.delete('shir', 1), 2), 3)
    '''

    self.createCodeFile(sourceCode)
    moudleName = "os"
    pattrenToSearch = "remove($all)"
    pattrenToReplace = "delete($all)"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

class ReplaceFuncParamsTests(UpdatorTests):
  def setUpClass():
    print("-----------------------------")
    print("Replace function params tests")
    print("-----------------------------")

  def test_replace_params_positions_when_params_are_int_variables(self):
    sourceCode = '''
      import math
      x = 2
      y = 3
      math.pow(x, y)     
    '''

    expectedConvertedCode = '''
      import math
      x = 2
      y = 3
      math.pow(y, x)
    '''

    self.createCodeFile(sourceCode)
    moudleName = "math"
    pattrenToSearch = "pow($1, $2)"
    pattrenToReplace = "pow($2, $1)"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_replace_params_positions_when_params_hard_coded_int(self):
    sourceCode = '''
      import math
      math.pow(2, 3)     
    '''

    expectedConvertedCode = '''
      import math
      math.pow(3, 2)
    '''

    self.createCodeFile(sourceCode)
    moudleName = "math"
    pattrenToSearch = "pow($1, $2)"
    pattrenToReplace = "pow($2, $1)"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_replace_params_positions_when_params_hard_coded_strings(self):
    sourceCode = '''
      import stringTool as stool
      stool.join('shir', 'binyamin')     
    '''

    expectedConvertedCode = '''
      import stringTool as stool
      stool.join('binyamin', 'shir')  
    '''

    self.createCodeFile(sourceCode)
    moudleName = "stringTool"
    pattrenToSearch = "join($1, $2)"
    pattrenToReplace = "join($2, $1)"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_replace_params_positions_pattern_inside_pattern(self):
    sourceCode = '''
      import math
      x = 2
      y = 3
      math.pow(math.pow(4, 5), y)
    '''

    expectedConvertedCode = '''
      import math
      x = 2
      y = 3
      math.pow(y, math.pow(5, 4))
    '''

    self.createCodeFile(sourceCode)
    moudleName = "math"
    pattrenToSearch = "pow($1, $2)"
    pattrenToReplace = "pow($2, $1)"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

class ChangeAttributeTests(UpdatorTests):
  def setUpClass():
    print("----------------------")
    print("Change attribute tests")
    print("----------------------")

  def test_rename_attr(self):
    sourceCode = '''
      import os
      os.path
    '''

    expectedConvertedCode = '''
      import os
      os.full_path
    '''

    self.createCodeFile(sourceCode)
    moudleName = "os"
    pattrenToSearch = "path"
    pattrenToReplace = "full_path"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_rename_attr_with_continuity(self):
    sourceCode = '''
      import os
      os.name.upper()
    '''

    expectedConvertedCode = '''
      import os
      os.full_name.upper()
    '''

    self.createCodeFile(sourceCode)
    moudleName = "os"
    pattrenToSearch = "name"
    pattrenToReplace = "full_name"
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_remove_attr(self):
    sourceCode = '''
      import os
      os.path
    '''

    expectedConvertedCode = '''
      import os
    '''

    self.createCodeFile(sourceCode)
    moudleName = "os"
    pattrenToSearch = "path"
    pattrenToReplace = ""
    execute(pattrenToSearch, pattrenToReplace, fileToConvert, moudleName)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)


