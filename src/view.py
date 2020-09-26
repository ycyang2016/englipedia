import requests

from ipywidgets import GridspecLayout
from IPython.display import display, Image
from ipywidgets.widgets import Checkbox, Label, Box, HBox, Button, Text, Layout, Output, HTML
from .dict import CamBridge, MerriamWebster, OnlineEtymology
from .util import myprint

class UI:

    def __init__(self):
        self.setting = self.create_settings()
        self.keyword = Text(value='', placeholder='Search dictionary and press enter', description='', disabled=False, layout=Layout(width='75%'))
        #self.search  = self.create_button('search')
        self.out     = Output()
        self.result  = {}

        self.keyword.on_submit(self.search)

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

    def show_result(self, event=None):
        if not self.result:
            return
        self.out.clear_output()
        fields = self.get_config()['fields']
        word_field = fields['Cambridge']['word']
        phrase_field = fields['Cambridge']['phrase']
        translate = fields['translate']['requirment']
        with self.out:
            for word in self.result.get('Cambridge', []):
                myprint(word['text'])
                myprint('(part-of-speech: {})'.format(word['pos']) if word_field['pos'] else '', end='\n')

                defines = word['defines'] if word_field['define'] else []
                for idx, define in enumerate(defines):
                    grammar = define.get('grammar', word.get('grammar', None))
                    myprint('define {}: {}'.format(idx, define['define']['text']), head=4)
                    myprint('({})'.format(define['define']['translate']) if translate and define['define']['text'] else '', head=1)
                    myprint('[{}]'.format(grammar) if word_field['grammar'] else '', end='\n', head=1)

                    examples = define['examples'] if word_field['examples'] else []
                    for ex_idx, example in enumerate(examples):
                        myprint('- example {}: {}'.format(ex_idx, example['text']), head=8)
                        myprint('({})'.format(example['translate']) if translate and example['text'] else '', end='\n', head=1)

                    phrases = define['phrases'] if phrase_field['text'] else []
                    for ph_idx, phrase in enumerate(phrases):
                        myprint('* phrase {}: {}'.format(ph_idx, phrase['phrase']), head=8, end='\n')
                        myprint('define: {}'.format(phrase['define']['text'] if phrase_field['define'] else ''), head=12)
                        myprint('({})'.format(phrase['define']['translate']) if translate and phrase_field['define'] else '', end='\n', head=1)

                        examples = phrase['examples'] if phrase_field['examples'] else []
                        for ex_idx, example in enumerate(examples):
                            myprint('- example {}: {}'.format(ex_idx, example['text']), head=16)
                            myprint('({})'.format(example['translate'] if translate and example['text'] else ''), end='\n', head=1)
                print()

            merriam_field = fields['Merriam']
            if self.result.get('Merriam') and (merriam_field['first use'] or merriam_field['etymology']):
                print('In Merriam webster:')
                if merriam_field['first use']:
                    myprint('First known use:', head=4, end='\n')
                    self.print_merriam(self.result['Merriam']['first_known_use'])

                if merriam_field['etymology']:
                    myprint('Etymology:', head=4, end='\n')
                    self.print_merriam(self.result['Merriam']['etymology'])


            etymology_field = fields['Etymology']
            if self.result.get('Etymology') and (etymology_field['description'] or etymology_field['image(if any)']):
                print('In etymology online:')
                if etymology_field['description']:
                    myprint('Description:', head=4, end='\n')
                    data = self.result['Etymology']['text']
                    myprint(data if data else 'No data', head=8, end='\n')
                if etymology_field['image(if any)'] and self.result['Etymology']['image_url']:
                    display(Image(requests.get(self.result['Etymology']['image_url']).content))

    def print_merriam(self, data):
        if data:
            for d in data:
                if d['type']:
                    myprint('part-of-speech: {}'.format(d['type']), head=8, end='\n')
                myprint(d['text'], head=8, end='\n')
                print()
        else:
            myprint(data if data else 'No data', head=4, end='\n')

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
            self.result = {}
            with self.out:
                for dict_name in dict_names:
                    print('search {}...'.format(dict_name))
                    self.result[dict_name] = engine[dict_name].search(self.keyword.value)
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
        button.on_click(self.search)
        return button

    def run(self):
        display(self.keyword)
        #display(self.search)
        display(self.setting)
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
