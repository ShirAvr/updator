import ast
import re

SINGLE_WILDCARD_ID = "__updator_wildcard"
MULTI_WILDCARD_ID = "__updator_multiwildcard"
MULTI_WILDCARD_SIGN = "$_"
SINGLE_WILDCARD_SIGN = "$"


def prepareRule(rule, module):
  newRule = {
    "patternToSearch": preparePattern(rule["patternToSearch"], module),
    "patternToReplace": preparePattern(rule["patternToReplace"], module)
  }

  return newRule

def preparePattern(pattern, module="", addAlias=True):
  if pattern is "":
    return None

  pattern = replacingWildCardSigns(pattern)

  if addAlias:
    pattern = addAliasToPatterns(pattern, module)
  pattern = ast.parse(pattern).body[0]

  if isinstance(pattern, ast.Expr):
    pattern = pattern.value
  if isinstance(pattern, (ast.Attribute, ast.Subscript)):
    del pattern.ctx

  return pattern

def createAssignmentRule(rule,  module, shouldBuild):
  if shouldBuild:
    assignmentPattern = createAssignmentPattern(rule,  module)
    patternToSearch = convertPatternToAssignment(rule["patternToSearch"], rule, module)
    patternToReplace = convertPatternToAssignment(rule["patternToReplace"], rule, module)
  else:
    assignmentPattern = handleAlias(rule["assignmentPattern"], rule["module"], module)
    patternToSearch = rule["patternToSearch"]
    patternToReplace = rule["patternToReplace"]

  # print("assignmentPattern: "+ assignmentPattern)
  # print("patternToSearch: "+ patternToSearch)
  # print("patternToReplace: "+ patternToReplace)

  rule = {
    "assignmentPattern": preparePattern(assignmentPattern, addAlias=False),
    "patternToSearch": preparePattern(patternToSearch, addAlias=False),
    "patternToReplace": preparePattern(patternToReplace, addAlias=False)
  }
  return rule

def createAssignmentPattern(rule,  module):
  return SINGLE_WILDCARD_SIGN + "1 = " + module + "." + rule["property"]

def convertPatternToAssignment(pattern, rule,  module):
  pattern = re.sub(r'['+SINGLE_WILDCARD_SIGN+']\\d', increaseWildcardNum, pattern)
  pattern = pattern.replace(rule["property"], SINGLE_WILDCARD_SIGN + "1")
  return pattern

def handleAlias(pattern, module,  alias):
  return pattern.replace(module, alias)

def increaseWildcardNum(matchedWildcard):
  variable_num = matchedWildcard.group()[1]
  return SINGLE_WILDCARD_SIGN + str(int(variable_num) + 1)

def replacingWildCardSigns(pattern):
  pattern = pattern.replace(MULTI_WILDCARD_SIGN, MULTI_WILDCARD_ID)
  pattern = re.sub(r'['+SINGLE_WILDCARD_SIGN+']\\d', defineWildcard, pattern)
  return pattern

def defineWildcard(matchedWildcard):
  variable_num = matchedWildcard.group()[1]
  return SINGLE_WILDCARD_ID + variable_num

def is_wildcard(patternNode):
  is_wildcard = patternNode.id[:-1] == SINGLE_WILDCARD_ID
  is_multi_wildcard = patternNode.id == MULTI_WILDCARD_ID
  return is_wildcard or is_multi_wildcard

def is_single_wildcard(patternNode):
  patternNode = patternNode[:-1]
  return patternNode in [SINGLE_WILDCARD_ID, MULTI_WILDCARD_ID]

def is_multi_wildcard(patternNode):
  return patternNode is MULTI_WILDCARD_ID

def addAliasToPatterns(pattern, moduleAlias):
  return moduleAlias + "." + pattern;

