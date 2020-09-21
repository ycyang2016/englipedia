from util import download_page


class CamBridge:

	base_url = 'https://dictionary.cambridge.org/dictionary/'

	def __init__(self, language):
		self.prefix_url = self.base_url + 'english-{language}/'.format(language=language.strip())

	def search(self, keyword):
		words = (word.strip() for word in keyword.split())
		doc = download_page(self.prefix_url + '-'.join(words))
		print(doc)


if __name__ == '__main__':

	dictionary = CamBridge('chinese-traditional')
	dictionary.search('hello')