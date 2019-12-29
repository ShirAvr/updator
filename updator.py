import astcompare, ast
from astcompare import assert_ast_like
import astor
import os.path
import sys
import tokenize
import warnings
import re
import copy
from functools import partial

__version__ = '0.1'

class ASTPatternConverter(object):
    """Scans Python code for AST nodes matching pattern.

    :param ast.AST pattern: The node pattern to search for
    """
    def __init__(self, pattrenToSearch, patternToReplace, patternVars={}):
        self.pattrenToSearch = pattrenToSearch
        self.patternToReplace = patternToReplace
        self.variables = patternVars

    def scan_ast(self, tree):
        """Walk an AST and yield nodes matching pattern.
        :param ast.AST tree: The AST in which to search
        """
        patternSelf = self
        pattrenToSearch = self.pattrenToSearch
        patternToReplace = self.patternToReplace
        nodetype = type(pattrenToSearch)

        # print("patternToReplace: "+ ast.dump(patternToReplace))

        class convertTree(ast.NodeTransformer):
            def visit(self, node):
                ast.NodeVisitor.visit(self, node)

                if isinstance(node, nodetype) and astcompare.is_ast_like(node, pattrenToSearch, patternSelf.variables):
                    # print("found node: " + ast.dump(node))
                    if patternToReplace is not None and patternSelf.variables != {}:
                      newNode = ASTPatternConverter.fillVariables(patternSelf, node, patternToReplace)
                      newNode = ast.copy_location(newNode, node) # not sure it's needed
                    else:
                      newNode = patternToReplace

                    # print("new node: " + ast.dump(newNode))

                    return newNode
                elif patternSelf.isInvalidNode(node):
                  return None
                else:
                  return node

        convertTree().visit(tree)

    def fillVariables(self, foundNode, patternToReplace):
        variables = self.variables
        patternSelf = self

        if variables == {}:
          return patternToReplace

        class retransformPattern(ast.NodeTransformer):
            def visit_Name(self, node):
                # print(variables)

                # and isinstance(variables, list) and variables != []
                if patternSelf.is_wildcard(node):
                    # print("variables[node.id]")
                    # print(variables[node.id])
                    return variables[node.id]
                else:
                    return node

        patternToReplace = copy.deepcopy(patternToReplace)
        return retransformPattern().visit(patternToReplace)

    def is_wildcard(self, node):
        is_wildcard = node.id[:-1] == WILDCARD_NAME
        is_multi_wildcard = node.id == MULTIWILDCARD_NAME
        return is_wildcard or is_multi_wildcard

    def scan_file(self, file):
      """Parse a file and yield AST nodes matching pattern.

      :param file: Path to a Python file, or a readable file object
      """
      if isinstance(file, str):
        with open(file, 'rb') as f:
          tree = ast.parse(f.read())
      else:
        tree = ast.parse(file.read())
      yield from self.scan_ast(tree)

    def filter_subdirs(self, dirnames):
        dirnames[:] = [d for d in dirnames if d != 'build']

    def scan_directory(self, directory):
        """Walk files in a directory, yielding (filename, node) pairs matching
        pattern.

        :param str directory: Path to a directory to search

        Only files with a ``.py`` or ``.pyw`` extension will be scanned.
        """
        for dirpath, dirnames, filenames in os.walk(directory):
            self.filter_subdirs(dirnames)

            for filename in filenames:
                if filename.endswith(('.py', '.pyw')):
                    filepath = os.path.join(dirpath, filename)
                    try:
                        for match in self.scan_file(filepath):
                            yield filepath, match
                    except SyntaxError as e:
                        warnings.warn("Failed to parse {}:\n{}".format(filepath, e))

    def isInvalidNode(self, node):
      return isinstance(node, ast.Expr) and self.isInvalidExpr(node)

    def isInvalidExpr(self, expNode):
      try:
        expNode.value
      except:
        return True

      return False


WILDCARD_NAME = "__updator_wildcard"
MULTIWILDCARD_NAME = "__updator_multiwildcard"

# WILDCARD_SIGN = "$"
MULTIWILDCARD_SIGN = "$all"

def prepare_pattern(s, _vars=[], moudleAlias=""):
    """Turn a string pattern into an AST pattern

    This parses the string to an AST, and generalises it a bit for sensible
    matching. ``?`` is treated as a wildcard that matches anything. Names in
    the pattern will match names or attribute access (i.e. ``foo`` will match
    ``bar.foo`` in files).
    """
    s = addAliasToPatterns(s, moudleAlias)
    s = replacingWildCardSigns(s)

    pattern = ast.parse(s).body[0]
    if isinstance(pattern, ast.Expr):
        pattern = pattern.value
    if isinstance(pattern, (ast.Attribute, ast.Subscript)):
        # If the root of the pattern is like a.b or a[b], we want to match it
        # regardless of context: `a.b=2` and `del a.b` should match as well as
        # `c = a.b`
        del pattern.ctx
    # return TemplatePruner(_vars=_vars).visit(pattern)
    return pattern

def defineWildcard(matchedWildcard):
    variable_num = matchedWildcard.group()[1]
    return WILDCARD_NAME + variable_num

def replacingWildCardSigns(pattern):
    pattern = pattern.replace(MULTIWILDCARD_SIGN, MULTIWILDCARD_NAME)
    pattern = re.sub(r'[$]\d', defineWildcard, pattern)
    return pattern

def prepareReplacingPattern(pattrenToReplace, moudleAlias):
  if pattrenToReplace is "":
    return None

  pattrenToReplace = replacingWildCardSigns(pattrenToReplace)

  # class AttrLister(ast.NodeVisitor):
  #     def visit_Attribute(self, node):
  #         global attrPattern
  #         attrPattern = node
  #         self.generic_visit(node)

  # class CallLister(ast.NodeVisitor):
  #     def visit_Call(self, node):
  #         global callPattern
  #         callPattern = node
  #         self.generic_visit(node)

  pattrenToReplace = addAliasToPatterns(pattrenToReplace, moudleAlias)
  pattrenToReplace = ast.parse(pattrenToReplace)
  # CallLister().visit(pattrenToReplace)
  return pattrenToReplace
  # return callPattern

def addAliasToPatterns(pattern, moudleAlias):
    return moudleAlias + "." + pattern;

def execute(pattrenToSearch, pattrenToReplace, filepath, givenMoudleName):
    with open(filepath, 'rb') as f:
        tree = ast.parse(f.read())

    moudleAlias = findMoudleAlias(tree, givenMoudleName)

    if moudleAlias is None:
      return

    patternVars = {}

    pattrenToSearch = prepare_pattern(pattrenToSearch, patternVars, moudleAlias)
    # print("pattrenToSearch: " + ast.dump(pattrenToSearch))
    pattrenToReplace = prepareReplacingPattern(pattrenToReplace, moudleAlias)
    patternConverter = ASTPatternConverter(pattrenToSearch, pattrenToReplace, patternVars)

    # print("=========== before ==========")
    # print(ast.dump(tree))
    # print("==============================")
    
    patternConverter.scan_ast(tree)
    
    # print("=========== after: ==========")
    # print(ast.dump(tree))
    # print("============================")

    convertedCode = astor.to_source(tree)
    saveConvertedCode(filepath, convertedCode)

def saveConvertedCode(filepath, convertedCode):
  with open(filepath, 'w') as f:
      f.write(convertedCode)
      f.close()

def findMoudleAlias(tree, givenMoudleName):
    class AliasFinder(ast.NodeVisitor):

      def __init__(self, givenMoudleName):
        super(AliasFinder, self).__init__()
        self.givenMoudleName = givenMoudleName;
        self.aliasMoudleName = None;

      def visit_alias(self, node):
          if (node.name is self.givenMoudleName and node.asname is not None):
            self.aliasMoudleName = node.asname
          elif (node.name is self.givenMoudleName and node.asname is None):
            self.aliasMoudleName = node.name

      def get_found_alias(self):
        return self.aliasMoudleName

    class ImportFinder(ast.NodeVisitor):
      def __init__(self, givenMoudleName):
        super(ImportFinder, self).__init__()
        self.givenMoudleName = givenMoudleName;
        self.aliasFinderClass = AliasFinder(self.givenMoudleName)

      def visit_Import(self, node):
        self.aliasFinderClass.visit(node)

      def get_found_alias(self):
        return self.aliasFinderClass.get_found_alias()

    aliasFinderClass = ImportFinder(givenMoudleName)
    aliasFinderClass.visit(tree)
    return aliasFinderClass.get_found_alias()

def main(argv=None):
    """Run astsearch from the command line.

    :param list argv: Command line arguments; defaults to :data:`sys.argv`
    """
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('pattern',
                    help="AST pattern to search for; see docs for examples")
    ap.add_argument('path', nargs='?', default='.',
                    help="file or directory to search in")
    ap.add_argument('-l', '--files-with-matches', action='store_true',
                    help="output only the paths of matching files, not the "
                         "lines that matched")
    ap.add_argument('--debug', action='store_true', help=argparse.SUPPRESS)

    args = ap.parse_args(argv)
    ast_pattern = prepare_pattern(args.pattern)
    if args.debug:
        print(ast.dump(ast_pattern))

    patternfinder = ASTPatternFinder(ast_pattern)

    def _printline(node, filelines):
        print("{:>4}|{}".format(node.lineno, filelines[node.lineno-1].rstrip()))

    current_filelines = []
    if os.path.isdir(args.path):
        # Search directory
        current_filepath = None
        if args.files_with_matches:
            for filepath, node in patternfinder.scan_directory(args.path):
                if filepath != current_filepath:
                    print(filepath)
                    current_filepath = filepath
        else:
            for filepath, node in patternfinder.scan_directory(args.path):
                if filepath != current_filepath:
                    with tokenize.open(filepath) as f:
                        current_filelines = f.readlines()
                    if current_filepath is not None:
                        print()  # Blank line between files
                    current_filepath = filepath
                    print(filepath)
                _printline(node, current_filelines)

    elif os.path.exists(args.path):
        # Search file
        if args.files_with_matches:
            try:
              node = next(patternfinder.scan_file(args.path))
            except StopIteration:
              pass
            else:
              print(args.path)
        else:
            for node in patternfinder.scan_file(args.path):
                if not current_filelines:
                    with tokenize.open(args.path) as f:
                        current_filelines = f.readlines()
                _printline(node, current_filelines)
                #print(ast.dump(node))

    else:
        sys.exit("No such file or directory: {}".format(args.path))

if __name__ == '__main__':
    main()
