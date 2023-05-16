import torch
from transformers import PegasusForConditionalGeneration, PegasusTokenizer

def load_tokenizer(config):
    print('Loading Tokenizer...', end='')
    tokenizer = PegasusTokenizer.from_pretrained(config['summarizer_model_name'])
    print('Done!')
    return tokenizer

def load_model(config):
    print('Loading Summarizer Model...', end='')
    torch_device = 'mps'
    model = PegasusForConditionalGeneration.from_pretrained(config['summarizer_model_name']).to(torch_device)
    print('Done!')
    return model

from tqdm import tqdm
class DocumentSummarizer():
    def __init__(self, config):
    # self.model_name = config['summarizer_model_name']
        self.torch_device = 'mps'
        #self.model = model
        #self.tokenizer = tokenizer
        self.path = config['summarized_text_path']
        self.chunk_size = int(config['chunk_size'])
        self.max_out_length = int(config['max_summary_length'])
        self.tokenizer = load_tokenizer(config)
        self.model = load_model(config)

    def get_response(self, input_text):
        batch = self.tokenizer([input_text],truncation=True,padding='longest',max_length=self.chunk_size, return_tensors="pt").to(self.torch_device)
        gen_out = self.model.generate(**batch,max_length=self.max_out_length,num_beams=5, num_return_sequences=1, temperature=1.5)
        output_text = self.tokenizer.batch_decode(gen_out, skip_special_tokens=True)
        return output_text   

    def run_on_documents(self, documents):
    # Runs on documents

    # If documents is a path
        if type(documents) == str:
            does_file_exist = os.path.isfile(documents)
            if not does_file_exist:
                raise ValueError('The path specified does not exist.')

            with open(documents, 'r') as f:
                documents = f.read()

            documents = documents.split('|')
        else:
            documents = [d.page_content for d in documents]

        self.summarized = []
        for doc in tqdm(documents):
            resp = self.get_response(doc)
            self.summarized.extend(resp)

        return self.summarized

    def save(self):
        with open(self.path, 'wt') as f:
            f.write('|'.join(self.summarized))

#ds.save()
