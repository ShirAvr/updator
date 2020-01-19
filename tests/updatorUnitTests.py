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

  def insertRule(self, rule):
    self.dbInterface.insertRule(rule)

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

  def test_module_name_unused_in_source_code(self):
    sourceCode = '''
      import math
      x = 2
      y = 3
      math.pow(x, y)     
    '''

    expectedConvertedCode = sourceCode

    rule = { "module": "math", 
             "patternToSearch": "pow($_)", 
             "patternToReplace": "pow2($_)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    moduleName = "sys"
    main(moduleName, fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_module_name_with_alias(self):
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

    rule = { "module": "math", 
             "patternToSearch": "pow($_)", 
             "patternToReplace": "pow2($_)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    moduleName = "math"
    main(moduleName, fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

class RenameFunctionTests(UpdatorTests):
  def setUpClass():
    print("-------------------------------")
    print("Rename function tests")
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

    rule = { "module": "os", 
             "patternToSearch": "remove()", 
             "patternToReplace": "delete()" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("os", fileToConvert)
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

    rule = { "module": "os", 
         "patternToSearch": "remove($1, $2)", 
         "patternToReplace": "delete($1, $2)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("os", fileToConvert)
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

    rule = { "module": "os", 
         "patternToSearch": "remove($_)", 
         "patternToReplace": "delete($_)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("os", fileToConvert)
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

    rule = { "module": "os", 
         "patternToSearch": "remove($1, $2)", 
         "patternToReplace": "delete($2, $1)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("os", fileToConvert)
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

    rule = { "module": "math", 
         "patternToSearch": "pow()", 
         "patternToReplace": "pow2()" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("math", fileToConvert)
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

    rule = { "module": "math", 
         "patternToSearch": "pow($1, $2, $3)", 
         "patternToReplace": "pow2()" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("math", fileToConvert)
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

    rule = { "module": "math", 
         "patternToSearch": "pow($1)", 
         "patternToReplace": "pow2()" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("math", fileToConvert)
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

    rule = { "module": "os", 
         "patternToSearch": "remove($_)", 
         "patternToReplace": "delete($_)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("os", fileToConvert)
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

    rule = { "module": "os", 
         "patternToSearch": "remove($_)", 
         "patternToReplace": "delete($_)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("os", fileToConvert)
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

    rule = { "module": "os", 
         "patternToSearch": "remove($_)", 
         "patternToReplace": "delete($_)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("os", fileToConvert)
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

    rule = { "module": "os", 
         "patternToSearch": "remove($_)", 
         "patternToReplace": "delete($_)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("os", fileToConvert)
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

    rule = { "module": "os", 
         "patternToSearch": "remove($_)", 
         "patternToReplace": "delete($_)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("os", fileToConvert)
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

    rule = { "module": "os", 
         "patternToSearch": "remove($_)", 
         "patternToReplace": "delete($_)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("os", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_apply_rule_change_function_inside_rule_inside_rule(self):
    sourceCode = '''
      import os
      os.remove(os.remove(os.remove('shir', 1), 2), 3)
    '''

    expectedConvertedCode = '''
      import os
      os.delete(3, os.delete(2, os.delete(1, 'shir')))
    '''

    rule = { "module": "os", 
         "patternToSearch": "remove($1, $2)", 
         "patternToReplace": "delete($2, $1)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("os", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

class RemoveFunctionTests(UpdatorTests):
  def setUpClass():
    print("-------------------------------")
    print("Remove function tests")
    print("-------------------------------")

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

    rule = { "module": "os", 
         "patternToSearch": "remove()", 
         "patternToReplace": "" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("os", fileToConvert)
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

    rule = { "module": "os", 
         "patternToSearch": "remove($_)", 
         "patternToReplace": "" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("os", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

class RemoveFunctionParamTests(UpdatorTests):
  def setUpClass():
    print("-------------------------------")
    print("Remove function params tests")
    print("-------------------------------")

  def test_remove_function_last_param(self):
    sourceCode = '''
      import os
      os.remove('shir', 'binyamin')        
    '''

    expectedConvertedCode = '''
      import os
      os.delete('shir')        
    '''

    rule = { "module": "os", 
         "patternToSearch": "remove($1, $2)", 
         "patternToReplace": "delete($1)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("os", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_remove_function_first_param(self):
    sourceCode = '''
      import os
      os.remove('shir', 'binyamin')        
    '''

    expectedConvertedCode = '''
      import os
      os.delete('binyamin')        
    '''

    rule = { "module": "os", 
         "patternToSearch": "remove($1, $2)", 
         "patternToReplace": "delete($2)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("os", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_remove_function_middle_param(self):
    sourceCode = '''
      import os
      os.remove('shir', 'binyamin', 'david')        
    '''

    expectedConvertedCode = '''
      import os
      os.delete('shir', 'david')        
    '''

    rule = { "module": "os", 
         "patternToSearch": "remove($1, $2, $3)", 
         "patternToReplace": "delete($1, $3)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("os", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_remove_function_middle_param_of_objects(self):
    sourceCode = '''
      import os
      os.remove(os.path, object(), object())
    '''

    expectedConvertedCode = '''
      import os
      os.delete(os.path, object())
    '''

    rule = { "module": "os", 
         "patternToSearch": "remove($1, $2, $3)", 
         "patternToReplace": "delete($1, $3)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("os", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_remove_all_function_params(self):
    sourceCode = '''
      import os
      os.remove(os.path, object(), object())
    '''

    expectedConvertedCode = '''
      import os
      os.delete()
    '''

    rule = { "module": "os", 
         "patternToSearch": "remove($_)", 
         "patternToReplace": "delete()" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("os", fileToConvert)
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

    rule = { "module": "math", 
             "patternToSearch": "pow($1, $2)", 
             "patternToReplace": "pow($2, $1)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("math", fileToConvert)
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

    rule = { "module": "math", 
             "patternToSearch": "pow($1, $2)", 
             "patternToReplace": "pow($2, $1)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("math", fileToConvert)
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

    rule = { "module": "stringTool", 
             "patternToSearch": "join($1, $2)", 
             "patternToReplace": "join($2, $1)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("stringTool", fileToConvert)
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

    rule = { "module": "math", 
             "patternToSearch": "pow($1, $2)", 
             "patternToReplace": "pow($2, $1)" }

    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("math", fileToConvert)
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

    rule = { "module": "os", "patternToSearch": "path", "patternToReplace": "full_path" }
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("os", fileToConvert)
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

    rule = { "module": "os", "patternToSearch": "name", "patternToReplace": "full_name" }
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("os", fileToConvert)
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

    rule = { "module": "os", "patternToSearch": "path", "patternToReplace": "" }
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    main("os", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

