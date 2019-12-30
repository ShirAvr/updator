"""Check Python ASTs against templates"""
import ast

WILDCARD_NAME = "__updator_wildcard"
MULTIWILDCARD_NAME = "__updator_multiwildcard"

def check_node_list(sample, template, variables, start_enumerate=0):
  """Check a list of nodes, e.g. function body"""
  if len(sample) != len(template):
    raise ASTMismatch(sample, template)

  for i, (sample_node, template_node) in enumerate(zip(sample, template), start=start_enumerate):
    if is_wildcard(template_node.id):
      treatWildcard(sample_node, variables, template_node.id)
    else:
      assert_ast_like(sample_node, template_node, variables)

def assert_ast_like(sample, template, variables):
  """Check that the sample AST matches the template.
  sample refers to source code tree.
  Raises a `ASTMismatch` if a difference is detected.
  """
  if not isinstance(sample, type(template)):
    raise ASTMismatch(sample, template)

  for name, template_field in ast.iter_fields(template):
    sample_field = getattr(sample, name)
    
    if isinstance(template_field, list):

      if template_field and isinstance(template_field[0], ast.AST):
        # if template_field[0].id is MULTIWILDCARD_NAME:
        if is_multi_wildcard(template_field[0].id):
          treatWildcard(sample_field, variables, template_field[0].id)
        else:
          check_node_list(sample_field, template_field, variables=variables)

      else:
        # List of plain values, e.g. 'global' statement names
        if sample_field != template_field:
          raise ASTMismatch(sample_field, template_field)

    elif isinstance(template_field, ast.AST):
      if isinstance(template_field, ast.Name) and is_wildcard(template_field.id):
        treatWildcard(sample_field, variables, template_field.id)

      assert_ast_like(sample_field, template_field, variables)
  
    else:
      # Single value, e.g. Name.id
      if sample_field != template_field:
          raise ASTMismatch(sample_field, template_field)

class ASTMismatch(AssertionError):
  """Exception for differing ASTs."""
  def __init__(self, got, expected):
    self.got = got
    self.expected = expected

  def __str__(self):
    return ("Mismatch - sample: " + self.got + ", template: " + self.expected)

def is_wildcard(wildcardName):
  wildcardName = wildcardName[:-1] 
  return wildcardName in [WILDCARD_NAME, MULTIWILDCARD_NAME]

def is_multi_wildcard(wildcardName):
  return wildcardName is MULTIWILDCARD_NAME

def treatWildcard(nodesToSave, variables, wildcardName):
  variables[wildcardName] = nodesToSave

def is_ast_like(sample, template, variables):
  """Returns True if the sample AST matches the template."""
  try:
    assert_ast_like(sample, template, variables)
    return True
  except ASTMismatch:
    return False
