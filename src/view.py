import requests

from ipywidgets import GridspecLayout
from IPython.display import display, Image
from ipywidgets.widgets import Checkbox, Label, Box, HBox, Button, Text, Layout, Output, HTML
from .dict import CamBridge, MerriamWebster, OnlineEtymology


class UI:

    def __init__(self):
        self.setting = self.create_settings()
        self.keyword = Text(value='', placeholder='Input Keyword', description='', disabled=False, layout=Layout(width='75%'))
        self.search  = self.create_button('search')
        self.out     = Output()
        self.result  = {}
        self.engine  = {
            'cambridge': CamBridge('chinese-traditional'),
            'merriam': MerriamWebster(),
            'etymology': OnlineEtymology()
        }

    def get_config(self):
        return {
            'dictionary': [dict_name.description for dict_name in self.setting[1, 1].children if dict_name.value],
            'fields': {
                'cambridge': {
                    'word'  : {dict_name.description: dict_name.value for dict_name in self.setting[3, 1].children},
                    'phrase': {dict_name.description: dict_name.value for dict_name in self.setting[4, 1].children}
                },
                'merriam': {dict_name.description: dict_name.value for dict_name in self.setting[5, 1].children},
                'etymology': {dict_name.description: dict_name.value for dict_name in self.setting[6, 1].children},
                'translate': {dict_name.description: dict_name.value for dict_name in self.setting[7, 1].children}
            }
        }

    def show_result(self, event=None):
        if not self.result:
            return
        self.out.clear_output()
        fields = self.get_config()['fields']
        word_field = fields['cambridge']['word']
        phrase_field = fields['cambridge']['phrase']
        translate = fields['translate']['requirment']
        with self.out:
            for word in self.result['cambridge']:
                print(word['text'], end='')
                if word_field['pos']:
                    print('', '(part-of-speech: {})'.format(word['pos']), end='')
                print()
                if word_field['define'] and len(word['defines']):
                    for idx, define in enumerate(word['defines']):
                        print('    define {}:'.format(idx), define['define']['text'], end='')
                        if translate:
                            print('', '({})'.format(define['define']['translate']['text']), end='')
                        if word_field['grammar'] and define.get('grammar', word.get('grammar', None)):
                            print('', '[{}]'.format(define.get('grammar', word.get('grammar', None))), end='')
                        print()
                        if word_field['examples']:
                            for eidx, example in enumerate(define['examples']):
                                print('        example {}:'.format(eidx), example['text'], end='')
                                if translate:
                                    print('', '({})'.format(example['translate']['text']), end='')
                                print()
                        if phrase_field['text']:
                            for pidx, phrase in enumerate(define['phrases']):
                                print('        phrase {}:'.format(pidx), phrase['phrase'])
                                if phrase_field['define']:
                                    print('            define:', phrase['define']['text'], end='')
                                    if translate:
                                        print('', '({})'.format(phrase['define']['translate']['text']), end='')
                                    print()
                                    if phrase_field['examples']:
                                        for eidx, example in enumerate(phrase['examples']):
                                            print('            example {}:'.format(eidx), example['text'], end='')
                                            if translate:
                                                print('', '({})'.format(example['translate']['text']), end='')
                                            print()
                print()
            merriam_field = fields['merriam']
            if merriam_field['first use'] or merriam_field['etymology']:
                print('In Merriam webster:')
                if merriam_field['first use']:
                    print('    First known use:')
                    print('       ', self.result['merriam']['first_known_use'])
                if merriam_field['etymology']:
                    print('    Etymology:')
                    print('       ', self.result['merriam']['etymology'])

            etymology_field = fields['etymology']
            if etymology_field['description'] or etymology_field['image(if any)']:
                print('In etymology online:')
                if etymology_field['description']:
                    print('    Description:')
                    print('       ', self.result['etymology']['text'])
                if etymology_field['image(if any)'] and self.result['etymology']['image_url']:
                    display(Image(requests.get(self.result['etymology']['image_url']).content))

    def search(self, event):
        self.out.clear_output()
        if self.keyword.value:
            self.result = {}
            for dict_name, search_engine in self.engine.items():
                self.result[dict_name] = search_engine.search(self.keyword.value)
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
        display(self.search)
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
