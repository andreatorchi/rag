from langchain_community.embeddings.ollama import OllamaEmbeddings

def get_embedding_function(conf:dict):

    if(conf["type"] == "ollama"):
        embeddings = OllamaEmbeddings(model=conf["model"])

    else:
        raise Exception("Embedding function not available")

    return embeddings