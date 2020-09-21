class Phrase:

	def __init__(self, text):
		self.text = text
		self.define = {}
		self.examples = []

	def add_define(self, language, define):
		self.define[language] = define

	def add_example(self, example):
		self.examples.append(example)

class Word:

	def __init__(self, text):
		self.text = text
		self.define = {}
		self.examples = []
		self.phrases  = []

	def add_define(self, language, define):
		self.define[language] = define

	def add_example(self, example):
		self.examples.append(example)

	def add_phrase(self, phrase):
		self.phrases.append(phrase)

class Noun(Word):

	def __init__(self, text, countable):
		super().__init__(text)
		self.countable = countable

class Verb(Word):

	def __init__(self, text, grama=None):
		super().__init__(text)
		self.grammar = grammar