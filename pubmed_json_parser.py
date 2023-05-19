import requests
import json

class PubmedJSONParser():
    def __init__(self, config):
        self.pmc_id = self.pmc_id = config['pmc_id']
        self.url = config['pmc_url']
        self.output_path = config['raw_text_path']
        print('*'*100)
        print('Parsing data from Pubmed')
        print('*'*100)
        self.fetch_json()
        self.format_json()
        self.clean_formatted_json()
        self.save_to_file()
        
    def fetch_json(self):
        print('Fetching data from PMC API...', end='')
        resp = requests.get(self.url.format(self.pmc_id))
        if resp.status_code == '404':
            raise ValueError('404 response from PMC API. Is the PMC id given correct?')
        self.data = resp.json()
        print('Done!')
        
    def format_json(self):
        print('Formatting data...', end='')
        output = {}
        text_type = self.data['documents'][0]['passages'][0]['text']
        curr_section_type = self.data['documents'][0]['passages'][0]['infons']['section_type']
        for passage in self.data['documents'][0]['passages']:
            if passage['infons']['section_type'] == 'TITLE':
                continue

            section_type = passage['infons']['section_type']
            if section_type not in output.keys():
                # print('Creating new section...')
                output[section_type] = {}
                text_type = passage['infons']['type']
                output[section_type][text_type] = []

            # In the event where the section has shown up before
            elif section_type != curr_section_type:
                text_type = passage['infons']['type']

            # print('*'*100)
            # print(passage['infons']['section_type'])
            # print(passage['infons']['type'])
            # print(passage['text'])

            if 'title' in passage['infons']['type'].lower():
                output[section_type][passage['text']] = []
                text_type = passage['text']
                # print('text type changed here to:', text_type)
            else:
                if text_type not in output[section_type].keys():
                    output[section_type][text_type] = []
                output[section_type][text_type].append(passage['text'])

            curr_section_type = section_type
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
        
    def save_to_file(self):
        print('Saving formatted JSON to ' + self.output_path + '...', end='')
        with open(self.output_path + '/' + self.pmc_id + '.json', 'w') as fp:
            json.dump(self.output, fp)
        print('Done!')