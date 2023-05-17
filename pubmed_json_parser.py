import requests
import json

class PubmedJSONParser():
    def __init__(self, url, pmc_id):
        self.pmc_id = pmc_id
        self.url = url.format(self.pmc_id)
        self.fetch_json()
        self.format_json()
        self.clean_formatted_json()
        
    def fetch_json(self):
        print('Fetching data from PMC API...', end='')
        resp = requests.get(self.url)
        if resp.status_code == '404':
            raise ValueError('404 response from PMC API. Is the PMC id given correct?')
        self.data = resp.json()
        print('Done!')
        
    def format_json(self):
        print('Formatting data...', end='')
        output = {}
        text_type = self.data['documents'][0]['passages'][0]['text']
        for passage in self.data['documents'][0]['passages']:
            if passage['infons']['section_type'] == 'TITLE':
                continue

            section_type = passage['infons']['section_type']
            if section_type not in output.keys():
                output[section_type] = {}
                text_type = passage['infons']['type']
                output[section_type][text_type] = []
            #print('*'*100)
            #print(passage['infons']['section_type'])
            #print(passage['infons']['type'])
            #print(passage['text'])

            if 'title' in passage['infons']['type'].lower():
                output[section_type][passage['text']] = []
                text_type = passage['text']
                #print('text type changed here to:', text_type)
            else:
                output[section_type][text_type].append(passage['text'])
                
        self.output = output
        print('Done!')
        
    def clean_formatted_json(self):
        print('Cleaning formatted JSON...', end='')
        for section, val in self.output.items():
            keys_to_remove = []
            for title, out in val.items():
                if len(out) == 0:
                    keys_to_remove.append(title)
                    
            for key in keys_to_remove:
                del val[key]
        print('Done!')            