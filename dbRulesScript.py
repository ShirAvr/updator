#!/usr/local/bin/python3

from updator.dbInterface import DbInterface

rules = [
  {
    "module": "os",
    "patternToSearch": "os.remove($_)",
    "patternToReplace": "os.delete($_)"
  },
  {
    "module": "os",
    "patternToSearch": "os.path",
    "patternToReplace": "os.full_path"
  },
  {
    "module": "math",
    "patternToSearch": "math.pow($1, $2)",
    "patternToReplace": "math.pow2($2, $1)"
  },
	{ 
		"module": "pandas",
    "patternToSearch": "pandas.config.build = True",
    "patternToReplace": "pandas.config.build = 'auto'" 
  },
  { 
  	"module": "pandas",
    "patternToSearch": "pandas.name = $1",
    "patternToReplace": "pandas.setName($1)" 
  },
  { 
    "module": "math",
    "patternToSearch": "[$1, $2] = math.getPosition()", 
    "patternToReplace": "[$2, $1] = math.getPosition()"
  },
  { 
    "module": "math",
    "property": "math.fmod",
    "patternToSearch": "math.fmod($1, $2)",
    "patternToReplace": "math.fmod($2, $1)",
    "assignmentRule": "auto"
	}
]

dbInterface = DbInterface()
dbInterface.dropRules()
dbInterface.insertRules(rules)
print("success")
