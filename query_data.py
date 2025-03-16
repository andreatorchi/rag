import argparse, yaml
from langchain.vectorstores.chroma import Chroma

from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from dependencies.modelFactory import *
from get_embedding_function import get_embedding_function



PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


with open('conf/conf.yaml') as file:
    conf = yaml.full_load(file)

def main():
    # Create CLI.

    query_text = "che genere di hypervisor è presente su ogni host fisico?"
    query_rag(query_text)[0]


def query_rag(query_text: str):

    # Prepare the DB.
    embedding_function = get_embedding_function(conf["embeddings"])
    db = Chroma(persist_directory=conf["db"]["path"], embedding_function=embedding_function) 

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    model = modelFactory.getModel(conf["model"]) #vaiton/minerva #ifioravanti/llamantino-2 #galatolo/cerbero-7b

    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("id", None) for doc, _score in results]

    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    return response_text, context_text


if __name__ == "__main__":
    main()