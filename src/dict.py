import logging

from copy import copy
from bs4  import BeautifulSoup
from .util import download_page, rebuild_string


class CamBridge:

    base_url = 'https://dictionary.cambridge.org/dictionary/'

    def __init__(self, language):
        self.prefix_url = self.base_url + 'english-{language}/'.format(language=language.strip())

    def extract_head(self, head):
        word = {
            'text': head.find('span', class_='hw dhw').text,
            'pos' : head.find('span', class_='pos dpos').text if head.find('span', class_='pos dpos') else None
        }

        if word['pos'] == 'verb':
            word['grammar'] = ' '.join(g.text for g in head.find_all('span', class_='gc dgc'))

        return word

    def extract_body(self, body):
        for def_block in body.find_all('div', class_='def-block ddef_block', recurisive=False):
            define    = rebuild_string(text.strip() for text in def_block.find('div', class_='ddef_h').find('div', class_='def ddef_d db').find_all(text=True) if text.strip())
            grammar   = def_block.find('span', class_='gc dgc')
            translate = def_block.find('div', class_='def-body ddef_b').find('span', class_='trans dtrans dtrans-se')
            examples  = []
            for example_soup in def_block.find_all('div', class_='examp dexamp'):
                eng_example   = rebuild_string(text.strip() for text in example_soup.find('span', class_='eg deg').find_all(text=True) if text.strip())
                trans_example = example_soup.find('span', class_='trans dtrans dtrans-se hdb')
                examples.append({
                    'text': eng_example,
                    'translate': {
                        'lang': trans_example['lang'],
                        'text': trans_example.text
                    }
                })

            body_data = {
                'define': {
                    'text': define,
                    'translate': {
                        'lang': translate['lang'],
                        'text': translate.text
                    }
                },
                'examples': examples,
                'phrases': []
            }

            if grammar:
                body_data['grammar'] = grammar.text

            if def_block.find_parent()['class'][0] == 'phrase-body':
                body_data['type'] = 'phrase'
                body_data['phrase'] = def_block.find_parent().previous_sibling.find('span', class_='phrase-title dphrase-title').text.strip()
            else:
                body_data['type'] = 'define'
            
            yield body_data

    def find_word(self, soup):
        for word_soup in soup.find_all('div', class_='pr entry-body__el'):
            word_head = word_soup.find('div', class_='pos-header dpos-h')
            word_body = word_soup.find('div', class_='pos-body')

            word = self.extract_head(word_head)
            word['defines'] = []
            for body in self.extract_body(word_body):
                if body.pop('type') == 'define':
                    word['defines'].append(body)
                else:
                    if not len(word['defines']):
                        word['defines'].append(body)
                    word['defines'][-1]['phrases'].append(body)

            yield word

    def search(self, keyword):
        target = '-'.join(word.strip() for word in keyword.split())
        soup   = BeautifulSoup(download_page(self.prefix_url + target), 'html.parser')
        logging.info('Search the query "{}" in CamBridge'.format(target))
        return list(self.find_word(soup))

class MerriamWebster:

    base_url = 'https://www.merriam-webster.com/dictionary/'

    def __init__(self):
        self.prefix_url = self.base_url

    def extract_body(self, soup, div_id, text_class):
        data_list = []
        anchor = soup.find('div', id=div_id)
        func_labels = anchor.find_all('p', class_='function-label')
        func_label_list = [] 
        if func_labels:
            for func_label in func_labels:
                sub_func_labels = func_label.findChildren('p', class_='function-label')
                for sub_func_label in sub_func_labels:
                    sub_func_label.extract()
                func_label_list.append(func_label)

            for func_label in func_label_list:
                text = func_label.find('p', class_=text_class).text
                type = func_label.text.replace(text, '').replace(' ', '')
                data_list.append(
                    {
                        'type': type,
                        'text': rebuild_string(text.strip() for text in text.split())
                    }
                )
        else:
            data_list.append(
                {
                    'type': None,
                    'text': rebuild_string(text.strip() for text in anchor.find('p', class_=text_class).text.split())
                }
            )    

        return data_list

    def search(self, keyword):
        target = '-'.join(word.strip() for word in keyword.split())
        logging.info('Search the query "{}" in Merriam-Webster'.format(target))
        soup = BeautifulSoup(download_page(self.prefix_url + target), 'html.parser')
        return {
            'first_known_use': self.extract_body(soup, div_id='first-known-anchor', text_class='ety-sl'),
            'etymology': self.extract_body(soup, div_id='etymology-anchor', text_class='et')
        }

class OnlineEtymology:

    base_url = 'https://www.etymonline.com/word/'

    def __init__(self):
        self.prefix_url = self.base_url

    def search(self, keyword):
        target = '-'.join(word.strip() for word in keyword.split())
        logging.info('Search the query "{}" in OnlineEtymology'.format(target))
        soup = BeautifulSoup(download_page(self.prefix_url + target), 'html.parser')
        word_label = soup.find('section', class_='word__defination--2q7ZH')
        chart_label = soup.find('div', class_='chart')

        return {
            'text': word_label.text if word_label else None,
            'image_url': chart_label.get('data-origin-path') if chart_label else None
        }
