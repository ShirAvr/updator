import ast
from astsearch1 import execute

moudleName = "sys"
codeMoudleName = None
attrPattern = None
callPattern = None

fileName = "./funcExample.py"
# codeToConvert = import "./pythonCodeExample.py"

# def checkMoudleName(tree):
	# for node in ast.walk(tree):
		#print(ast.dump(node))

		# for field in ast.iter_fields(node):
		# print(field)
		# print(node.body)
		# print("===")

# def checkMoudleName(tree):

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

print("=============")
print("moudle name: " + codeMoudleName)
print("=============")

pattrenToSearch = codeMoudleName + ".exc_info(??)"
pattrenToReplace = codeMoudleName + ".execute_info(v1)"
pattrenToReplace = ast.parse(pattrenToReplace)
CallLister().visit(pattrenToReplace)

# print("patternToReplace: "+ ast.dump(callPattern))

execute(pattrenToSearch, callPattern, fileName)

# print(ast.dump(tree.body[0]))
# checkMoudleName(tree)

# pattren1 = ast.parse("print()")
# pattren2 = ast.parse("scan()")
# astCodeToConvert = ast.parse(codeToConvert)


