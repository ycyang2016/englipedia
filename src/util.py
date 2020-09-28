import re
import sys
import requests


def download_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
    }
    data = requests.get(url, headers=headers).content
    return data

def rebuild_string(strings):
	parser = re.compile(r'^[\w ]*$')
	result = ''
	for string in strings:
		if parser.match(string):
			result += (string + ' ')
		else:
			result = result.strip() + string + ' '
	return result.strip()

def myprint(string='', head=0, end='', file=sys.stdout):
	print(' ' * head + string, end=end, file=file)