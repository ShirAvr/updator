import ast
import re

SINGLE_WILDCARD_ID = "__updator_wildcard"
MULTI_WILDCARD_ID = "__updator_multiwildcard"
MULTI_WILDCARD_SIGN = "$all"
SINGLE_WILDCARD_SIGN = "$"


def preparePattern(pattern, moudle):
  if pattern is "":
    return None

  pattern = replacingWildCardSigns(pattern)
  pattern = addAliasToPatterns(pattern, moudle)
  pattern = ast.parse(pattern).body[0]

  if isinstance(pattern, ast.Expr):
    pattern = pattern.value
  if isinstance(pattern, (ast.Attribute, ast.Subscript)):
    del pattern.ctx

  return pattern


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

def addAliasToPatterns(pattern, moudleAlias):
  return moudleAlias + "." + pattern;

