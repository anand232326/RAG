from dotenv import load_dotenv
import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchableField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
    VectorSearch,
    VectorSearchProfile
)

load_dotenv()


def create_index(endpoint:str,api_key:str,index_name:str,embedding_dimensions:int=1536)->None:
    pass