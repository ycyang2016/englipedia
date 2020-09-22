import logging

from bs4  import BeautifulSoup
from util import download_page


class CamBridge:

	base_url = 'https://dictionary.cambridge.org/dictionary/'

	def __init__(self, language):
		self.prefix_url = self.base_url + 'english-{language}/'.format(language=language.strip())

	def extract_head(self, head):
		return {
			'text': head.find('span', class_='hw dhw').text,
			'pos ': head.find('span', class_='pos dpos').text,
			'gram': ' '.join(g.text for g in head.find_all('span', class_='gc dgc'))
		}

	def extract_body(self, body):
		return {}

	def find_word(self, soup):
		for word_soup in soup.find_all('div', class_='pr entry-body__el'):
			word_head = word_soup.find('div', class_='pos-header dpos-h')
			word_body = word_soup.find('div', class_='pos-body')

			self.extract_head(word_head)
			self.extract_body(word_body)

			yield {}

	def search(self, keyword):
		target = '-'.join(word.strip() for word in keyword.split())
		soup   = BeautifulSoup(download_page(self.prefix_url + target), 'html.parser')
		for word_soup in self.find_word(soup):
			pass
		logging.info('Search the query "{}" in CamBridge'.format(target))

		#print(soup)


class MerriamWebster:

	base_url = 'https://www.merriam-webster.com/dictionary/'

	def __init__(self):
		self.prefix_url = self.base_url

	def search(self, keyword):
		target = '-'.join(word.strip() for word in keyword.split())
		logging.info('Search the query "{}" in Merriam-Webster'.format(target))
		soup = BeautifulSoup(download_page(self.prefix_url + target), 'html.parser')
		return {
			'first_known_use': soup.find('p', class_='ety-sl').text,
			'etymology': soup.find('p', class_='et').text
		}

if __name__ == '__main__':
	import log
	dictionary = CamBridge('chinese-traditional')
	dictionary.search('out of step')

	dictionary = MerriamWebster()
	dictionary.search('out of step')
