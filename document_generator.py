from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, NLTKTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
import os
import requests

class DocumentGenerator():
# Fetches raw text and creates vector embeddings
# that can be queried upon for a single PubMed article
# (Can be full text or abstract)

# Note: We can use an existing FAISS DB store here
# however, the embedding model must be the same as what
# is used to create the DB
# Additionally, the path to the existing db must be given as
# db_path, and 'use_existing_db' must be set to true.

# If a new db is to be created, it will be created at db_path.
# Warning: This will OVERWRITE any existing dbs at the path.
    def __init__(self,config):
        self.url = config['pmc_url']
        self.output_path = config['raw_text_path']
        self.chunk_size = int(config['chunk_size'])
        self.chunk_overlap = int(config['chunk_overlap'])
        self.model_name = config['embedding_model_name']
        self.db_path = config['db_path']
        self.use_existing_db = config['use_existing_db']
        self.pmc_id = config['pmc_id']
        self.top_k = int(config['top_k'])

        self.load_embedding_engine()

        if self.use_existing_db.lower() == 'true':
            self.load_db_from_existing_path()
        else:
            print('Creating new vector database')
            self.fetch_from_pmc()
            self.load_text_into_langchain()
            self.split_text_into_chunks()
            self.create_vector_embeddings()

    def fetch_from_pmc(self):
        print('Fetching raw text from PMC API...', end='')
        url = self.url.format(self.pmc_id)
        resp = requests.get(url)
        if resp.status_code == '404':
            raise ValueError('404 response from PMC API. Is the PMC id given correct?')

        data = resp.json()
        out = []
        for text in data['documents'][0]['passages']:
            if 'text' in text.keys():
                out.append(text['text'])

        outstr = '\n'.join(out)
        self.path = self.output_path + str(self.pmc_id) + '.txt'
        with open(self.path, 'wt') as f:
            f.write(outstr)
        print('Done!')

    def load_text_into_langchain(self):
        print('Reading the raw document into Langchain...', end='')
        loader = TextLoader(self.pmc_id +'.txt')
        self.documents = loader.load()
        print('Done!')

    def split_text_into_chunks(self):
        # Get your splitter ready
        print('Splitting raw document into chunks...', end='')
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)

        # Split your docs into texts
        self.texts = text_splitter.split_documents(self.documents)
        print (f"Done! You have {len(self.texts)} chunks")

    def load_embedding_engine(self):
    # Get embedding engine ready
        print('Loading Embedding Engine...', end='')
        self.model = HuggingFaceEmbeddings(model_name=self.model_name)
        print('Done!')

    def create_vector_embeddings(self):
    # Embed your texts
        print('Creating vector DB and embeddings for the texts...', end='')
        self.db = FAISS.from_documents(self.texts, self.model)
        self.db.save_local(self.db_path + self.pmc_id + '.db')
        print('Done!')

    def load_db_from_existing_path(self):
        print('Loading DB from existing path...', end='')
        does_file_exist = os.path.isfile(self.db_path)
        if not does_file_exist:
            raise ValueError('DB does not exist: There is no file at the path:', self.db_path)

        self.db = FAISS.load_local(self.db_path, self.model)
        print('Done!')

    def similarity_search(self, query):
        self.docs = self.db.similarity_search(query, k=self.top_k)
        self.docs = [d.page_content for d in self.docs]
        with open(self.output_path + self.pmc_id + '_' + query.replace(' ', '_') + '.txt', 'wt') as f:
            f.write('|'.join(self.docs))
        return self.docs
