import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import shutil

CHROMA_DIR="vector_db"
COLLECTION_NAME="product_data"
EMBEDDING_MODEL="BAAI/bge-small-en-v1.5"

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device":"cpu"}
    )

def build_vector(chunks: list) -> Chroma:

    print("Building vector store")

    embeddings = get_embeddings()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )

    vector_store.add_documents(documents=chunks)

    print(f"Successfully stored {len(chunks)} chunks")

    return vector_store

def load_vector_store()->Chroma:
    embeddings=get_embeddings()
    vector_store=Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )
    return vector_store

def get_retriver(vector_store:Chroma,k:int=10):
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k":k}
    )

def delete_vector_store():
    """Delete all locally stored research data."""

    if os.path.exists(CHROMA_DIR):
        shutil.rmtree(CHROMA_DIR)
        print("Research data deleted successfully.")
    else:
        print("No research data found.")