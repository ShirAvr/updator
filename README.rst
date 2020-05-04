Updator
-------

Always be up-to-date!

Updator is a tool to automatically upgrade python libraries.
It defines API changes rules which is actually python patterns (with some extras) that will transform into ast.
The rules were designed to be written by the libraries' authors, but that will happen later on.
What it does is basically just transform the python code that should be upgraded into an AST, and search the rules ast within the source code ast. If a rule ast is found - it's transform the pattern into the new pattern.

**Install the package:**


``pip install updator``

**To Use Updator:**


``updator run [lib] [path]``

where:
  - lib is the library you want to upgrade
  - path is the path for your code file you want to upgrade 
