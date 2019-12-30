import pymongo

class DbInterface:

	def __init__(self):
		client = pymongo.MongoClient('localhost', 27017)
		self.db = client.updator_db
		self.rules = self.db.rules
		self.createIndex()

	def dropRules(self):
		self.rules.drop()

	def createIndex(self):
		self.rules.create_index([("moudle", pymongo.ASCENDING), ("patternToSearch", pymongo.ASCENDING)], unique=True)

	def insertRule(self, rule):
		self.rules.insert_one(rule)

	def insertRules(self, rules):
		self.rules.insert_many(rules)

	def findRulesByMoudle(self, moudle):
		return self.rules.find({"moudle": moudle})

