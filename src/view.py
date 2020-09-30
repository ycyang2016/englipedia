import os
import sys
import requests

from ipywidgets import GridspecLayout
from IPython.display import display, Image, FileLink
from ipywidgets.widgets import Checkbox, Label, Box, HBox, Button, Textarea, Layout, Output, HTML
from .dict import CamBridge, MerriamWebster, OnlineEtymology
from .util import myprint

class UI:

    def __init__(self):
        self.setting = self.create_settings()
        self.keyword = Textarea(value='', placeholder='Search dictionary and press enter', description='', disabled=False, rows=1, layout=Layout(width='50%'))
        self.search_button  = self.create_button('search')
        self.save_button  = self.create_button('save file')
        self.out     = Output()
        self.results = {}

        self.search_button.on_click(self.search)
        self.save_button.on_click(self.save_file)
        self.keyword.observe(self.adjust_keyword_size, 'value')

    def adjust_keyword_size(self, event):
        self.keyword.rows = self.keyword.value.count('\n') + 1

    def save_file(self, event):
        filename = 'result.txt'
        with open(filename, 'w') as fp:
            self.show_result(file=fp)
        self.out.clear_output()

    def get_config(self):
        return {
            'dictionary': [dict_name.description for dict_name in self.setting[1, 1].children if dict_name.value],
            'fields': {
                'Cambridge': {
                    'word'  : {dict_name.description: dict_name.value for dict_name in self.setting[3, 1].children},
                    'phrase': {dict_name.description: dict_name.value for dict_name in self.setting[4, 1].children}
                },
                'Merriam': {dict_name.description: dict_name.value for dict_name in self.setting[5, 1].children},
                'Etymology': {dict_name.description: dict_name.value for dict_name in self.setting[6, 1].children},
                'translate': {dict_name.description: dict_name.value for dict_name in self.setting[7, 1].children}
            }
        }

    def show_result(self, event=None, file=sys.stdout):
        if not self.results:
            return
        self.out.clear_output()
        fields = self.get_config()['fields']
        word_field = fields['Cambridge']['word']
        phrase_field = fields['Cambridge']['phrase']
        translate = fields['translate']['requirment']
        with self.out:
            for keyword, result in self.results.items():
                myprint(keyword + ':', end='\n', file=file)
                myprint('*' * 10, end='\n', file=file)
                for word in result.get('Cambridge', []):
                    myprint(word['text'], head=4, file=file)
                    myprint('(part-of-speech: {})'.format(word['pos']) if word_field['pos'] else '', end='\n', file=file)

                    defines = word['defines'] if word_field['define'] else []
                    for idx, define in enumerate(defines):
                        grammar = define.get('grammar', word.get('grammar', None))
                        myprint('define {}: {}'.format(idx, define['define']['text']), head=8, file=file)
                        myprint('({})'.format(define['define']['translate']) if translate and define['define']['text'] else '', head=1, file=file)
                        myprint('[{}]'.format(grammar) if word_field['grammar'] else '', end='\n', head=1, file=file)

                        examples = define['examples'] if word_field['examples'] else []
                        for ex_idx, example in enumerate(examples):
                            myprint('- example {}: {}'.format(ex_idx, example['text']), head=12, file=file)
                            myprint('({})'.format(example['translate']) if translate and example['text'] else '', end='\n', head=1, file=file)

                        phrases = define['phrases'] if phrase_field['text'] else []
                        for ph_idx, phrase in enumerate(phrases):
                            myprint('* phrase {}: {}'.format(ph_idx, phrase['phrase']), head=12, end='\n', file=file)
                            myprint('define: {}'.format(phrase['define']['text'] if phrase_field['define'] else ''), head=16, file=file)
                            myprint('({})'.format(phrase['define']['translate']) if translate and phrase_field['define'] else '', end='\n', head=1, file=file)

                            examples = phrase['examples'] if phrase_field['examples'] else []
                            for ex_idx, example in enumerate(examples):
                                myprint('- example {}: {}'.format(ex_idx, example['text']), head=20, file=file)
                                myprint('({})'.format(example['translate'] if translate and example['text'] else ''), end='\n', head=1, file=file)
                    myprint(end='\n', file=file)

                merriam_field = fields['Merriam']
                if result.get('Merriam') and (merriam_field['first use'] or merriam_field['etymology']):
                    myprint('In Merriam webster:', end='\n', head=4, file=file)
                    if merriam_field['first use']:
                        myprint('First known use:', head=8, end='\n', file=file)
                        self.print_merriam(result['Merriam']['first_known_use'], file=file)

                    if merriam_field['etymology']:
                        myprint('Etymology:', head=8, end='\n', file=file)
                        self.print_merriam(result['Merriam']['etymology'], file=file)

                etymology_field = fields['Etymology']
                if result.get('Etymology') and (etymology_field['description'] or etymology_field['image(if any)']):
                    myprint('In etymology online:', end='\n', head=4, file=file)
                    if etymology_field['description']:
                        myprint('Description:', head=8, end='\n', file=file)
                        data = result['Etymology']['text']
                        myprint(data if data else 'No data', head=12, end='\n', file=file)
                    if etymology_field['image(if any)'] and result['Etymology']['image_url']:
                        display(Image(requests.get(result['Etymology']['image_url']).content))
                        myprint(end='\n', file=file)
                myprint('=' * 75, end='\n', file=file)

    def print_merriam(self, data, file=sys.stdout):
        if data:
            for d in data:
                if d['type']:
                    myprint('part-of-speech: {}'.format(d['type']), head=12, end='\n', file=file)
                myprint(d['text'], head=12, end='\n', file=file)
                myprint(file=file)
        else:
            myprint(data if data else 'No data', head=8, end='\n', file=file)

    def search(self, event):
        self.out.clear_output()
        config = self.get_config()
        dict_names = config['dictionary']
        engine  = {
            'Cambridge': CamBridge('chinese-traditional' if config['fields']['translate']['requirment'] else None ),
            'Merriam': MerriamWebster(),
            'Etymology': OnlineEtymology()
        }
        if self.keyword.value:
            self.results = {}
            with self.out:
                for keyword in self.keyword.value.split('\n'):
                    print('search {}...'.format(keyword))
                    self.results[keyword] = {dict_name : engine[dict_name].search(keyword.strip()) for dict_name in dict_names}
                self.show_result()
        else:
            with self.out:
                print('The keyword in search bar is required.')

    def create_settings(self):
        word       = self.create_checkbox('define', 'pos', 'grammar', 'examples')
        phrase     = self.create_checkbox('text', 'define', 'examples')
        dictionary = self.create_checkbox('Cambridge', 'Merriam', 'Etymology')
        merriam    = self.create_checkbox('first use', 'etymology')
        etymology  = self.create_checkbox('description', 'image(if any)')
        translate  = self.create_checkbox('requirment')

        setting    = GridspecLayout(8, 6)
        setting[0, 2] = Label('settings')
        setting[1, 1:len(dictionary) + 1] = Box(dictionary)
        setting[1, 0] = Label('dictionary')
        setting[2, 2] = Label('output')
        setting[3, 0] = Label('word')
        setting[3, 1:len(word) + 1] = Box(word)
        setting[4, 0] = Label('phrase')
        setting[4, 1:len(phrase) + 1] = Box(phrase)
        setting[5, 0] = Label('Merriam')
        setting[5, 1:len(merriam) + 1] = Box(merriam)
        setting[6, 0] = Label('Etymology')
        setting[6, 1:len(etymology) + 1] = Box(etymology)
        setting[7, 0] = Label('Translate')
        setting[7, 1:len(translate) + 1] = Box(translate)
        return setting

    def create_checkbox(self, *options, default=True):
        box = [Checkbox(value=default, description=dict_name, disabled=False, indent=False) for dict_name in options]
        for c in box:
            c.observe(self.show_result)
        return box

    def create_button(self, name):
        button = Button(description=name, disabled=False, button_style='info', tooltip='Click me', icon='')
        return button

    def run(self):
        display(self.keyword)
        display(self.search_button)
        display(self.setting)
        display(self.save_button)
        display(self.out)

        style = """
            <style>
            .jupyter-widgets-output-area .output_scroll {
                height: unset !important;
                border-radius: unset !important;
                -webkit-box-shadow: unset !important;
                box-shadow: unset !important;
            }
            .jupyter-widgets-output-area  {
                  height: auto !important;
            }
         </style>
        """
        display(HTML(style))
