import argparse, yaml, os
import shutil
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from langchain.vectorstores.chroma import Chroma
from docling_export import export_documents


with open('conf/conf.yaml') as file:
    conf = yaml.full_load(file)

def populate_database(input_path, input_filename, clear_db=False):

    if(clear_db):
        clear_database(conf["db"]["path"])
    # Create/update the data store.
    documents = load_documents(input_path, input_filename)
    
    chunks = split_documents(documents)
    add_to_db(chunks)


def load_documents(input_path, input_filename):
    document_loader = TextLoader(os.path.join(input_path, input_filename))
    return document_loader.load()


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def add_to_db(chunks: list[Document]):
    # Load the existing database.
    embedding_function=get_embedding_function(conf["embeddings"])
    db = Chroma(persist_directory=conf["db"]["path"], embedding_function=embedding_function)

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        db.persist()
    else:
        print("No new documents to add")


def calculate_chunk_ids(chunks):

    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks

def clear_database(path):
    if os.path.exists(path):
        shutil.rmtree(path)

if __name__ == "__main__":

    input_path = conf["data_path"]["input_path"]
    export_output_path = conf["data_path"]["export_output_path"]
    export_output_filename = conf["data_path"]["export_output_filename"]
    cleaned_output_filename  = export_output_filename.split(".")[0] + "_cleaned.txt" #"ISTRUZIONE_OPERATIVA_CREAZIONE_VM_CLOUD_INSIEL_REV_00-with-image-refs_cleaned.txt"

    export_documents(input_path, export_output_path, export_output_filename)
    
    from clean_data import *
    cleaner = basicDataCleaner()
    cleaner.clean(os.path.join(export_output_path, export_output_filename), os.path.join(export_output_path, cleaned_output_filename))

    
    populate_database(export_output_path, cleaned_output_filename)