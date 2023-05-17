# clinical_trial_data_extractor
Pipelines built on Langchain and Huggingface Transformers for document localization of Pubmed Open Access (PMC) literature.

### Introduction
This is a set of small pipelines written over the langchain library and huggingface transformers for unsupervised document localization. Document localization is the problem where we want to find the exact relevant section of a long article that answers a specific query or need.

### Process
PMC Document Extraction: We fetch PMC open access articles (using BioC REST API) given a PMC id. We convert them into a simplified JSON format with section headers and titles, and paragraphs (as given by PMC).

Document Feature Generation/Vector Store creation: We use FAISS index through the Langchain library (and a sentence-transformers model) to create a vector store for each paragraph in the article. Using Langchain and the vector store we can then find the most relevant document (using similarity_search) to a query.

The aim is to feed these relevant texts to a Large Language Model such as GPT-3 to create JSON data for very specific requirements. For example, in this extractor my target is to find the arms, procedures, and frequency of procedures for a specific clinical trial. Through the localization module above I can identify the relevant sections of a very large document, whch is then given to GPT to extract the relevant arms, procedures and frequencies. 


