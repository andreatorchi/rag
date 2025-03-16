
from langchain_community.llms.ollama import Ollama

class model():

    def invoke(self):
        pass

class ollamaModel(model):

    def __init__(self, conf):
        super()
        self.model = Ollama(model=conf["name"])

    def invoke(self, prompt:str):
        return self.model.invoke(prompt)