from .model import *

class modelFactory():

    def getModel(conf):
        available_models = { "ollama" : ollamaModel}

        if conf["type"] in available_models:
            return available_models[conf["type"]](conf)
        
        else:
            raise Exception("model not available")