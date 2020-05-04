update: 

The function get the source code tree T (ast.Ast) and the set of rules, and apply the pattern match. for each rule, update the source tree T according to the new pattern. 
Arguments:
tree: source code in ast.AST representation 
rules: transformation rule object include two patterns - patternToSearch
and patternToReplace. While patternToSearch is the pattern we want to match with the tree and patternToReplace is the pattern we want to transform to. Both of the patterns are an ast.AST instances.

transform:

Traverse the nodes of the source code tree, each node it’s visit invoke isTreesEquals function. tree is the source code tree, starting with the root node. The function returns the result source code tree after applying the given transformation rule whenever a match is found.
Arguments:
tree: source code tree (ast.AST)
rule: transformation rule object include two patterns (ast.AST) -
patternToSearch and patternToReplace.



update(tree, rules):
	for rule in rules:
		transform(tree, rule)

	return tree

transform(tree, rule):
	for node in tree.getNodes():
		if isTreesEquals(node, rule.patternToSearch, vars):
			node = fillVars(rule.patternToReplace, vars)

fillVars(patternToReplace, vars):
	for node in patternToReplace.getNodes():
		if is_wildcard(node):
			node = vars[node]

isTreesEquals(sample, pattern, vars):
  try:
    assertTrees(sample, pattern, vars)
    return True
  except ASTMismatch:
    return False

assertTrees(sample, pattern, vars):
	for attr, patternNode in pattern.fields():
		sampleNode = getattr(sample, attr)

		if is_wildcard(patternNode):
			treatWildcard(vars, sampleNode, patternNode)

		if isinstance(patternNode, ast.AST):
			assertTrees(sampleNode, patternNode)

		else if not isObjectsEqual(sampleNode, patternNode):
			raise AstMismatch()

treatWildcard(vars, nodesToSave, wildcardKey):
  vars[wildcardKey] = nodesToSave



