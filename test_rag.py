from query_data import query_rag
from langchain_community.llms.ollama import Ollama
import yaml
from dependencies.modelFactory import *


CORRECTNESS_EVAL_PROMPT = """
Expected Response: {expected_response}
Actual Response: {actual_response}
---
(Answer with 'true' or 'false') Does the actual response match or contains the expected response? 
A value of True means that the answer meets all of the criteria.
A value of False means that the answer does not meet all of the criteria.
"""


RELEVANCE_EVAL_PROMPT = """
question: {question}
given response: {actual_response}
---
(Answer with 'true' or 'false') Is the given response relevant to the question useful to answer the question? 
A relevance value of True means that the answer meets all of the criteria.
A relevance value of False means that the answer does not meet all of the criteria.
"""


GROUNDEDNESS_EVAL_PROMPT = """
response: {actual_response}
given facts: {docs}
---
(Answer with 'true' or 'false') Is the given response relevant and grounded to the given facts ? 
A grounded value of True means that the answer meets all of the criteria.
A grounded value of False means that the answer does not meet all of the criteria.
"""


RETRIEVAL_RELEVANCE_EVAL_PROMPT = """
question: {question}
given facts: {docs}
---
(Answer with 'true' or 'false') Does the question provided contain ANY keywords or semantic meaning related to the question? 
It is OK if the facts have SOME information that is unrelated to the question as long as it contains some keywords that are semantically similar
Relevance:
A relevance value of True means that the FACTS contain ANY keywords or semantic meaning related to the QUESTION and are therefore relevant.
A relevance value of False means that the FACTS are completely unrelated to the QUESTION.
"""

with open('conf/conf.yaml') as file:
    conf = yaml.full_load(file)



def test_htpervisor():
    assert query_and_validate(
        question="che genere di hypervisor è presente su ogni host fisico?",
        expected_response="VMWare ESXi",
    )



def test_dns():
    assert query_and_validate(
        question="come viene fornito fornisce il servizio DNS? ",
        expected_response="Active Directory",
    )


def test_networking():
    assert query_and_validate(
        question="come viene gestito il networking ?",
        expected_response="NSX-T",
    )


def query_and_validate(question: str, expected_response: str):
    response_text, relevant_docs = query_rag(question)
    model = modelFactory.getModel(conf["model"]) #model = Ollama(model="ifioravanti/llamantino-2")

    prompt = CORRECTNESS_EVAL_PROMPT.format(expected_response=expected_response, actual_response=response_text)
    evaluation_results_str = model.invoke(prompt)
    evaluation_results_str_cleaned = evaluation_results_str.strip().lower()
    eval_test_response(prompt, evaluation_results_str_cleaned)

    prompt = RELEVANCE_EVAL_PROMPT.format(question=question, actual_response=response_text )
    evaluation_results_str = model.invoke(prompt)
    evaluation_results_str_cleaned = evaluation_results_str.strip().lower()
    eval_test_response(prompt, evaluation_results_str_cleaned)

    prompt = GROUNDEDNESS_EVAL_PROMPT.format(actual_response=response_text, docs=relevant_docs)
    evaluation_results_str = model.invoke(prompt)
    evaluation_results_str_cleaned = evaluation_results_str.strip().lower()
    eval_test_response(prompt, evaluation_results_str_cleaned)

    prompt = RETRIEVAL_RELEVANCE_EVAL_PROMPT.format(question=question, docs=relevant_docs)
    evaluation_results_str = model.invoke(prompt)
    evaluation_results_str_cleaned = evaluation_results_str.strip().lower()
    eval_test_response(prompt, evaluation_results_str_cleaned)

def eval_test_response(prompt, evaluation_results_str_cleaned):
    print(prompt)

    if "true" in evaluation_results_str_cleaned:
        # Print response in Green if it is correct.
        print("\033[92m" + f"Response: {evaluation_results_str_cleaned}" + "\033[0m")
        return True
    elif "false" in evaluation_results_str_cleaned:
        # Print response in Red if it is incorrect.
        print("\033[91m" + f"Response: {evaluation_results_str_cleaned}" + "\033[0m")
        return False
    else:
        print(evaluation_results_str_cleaned)
        raise ValueError(
            f"Invalid evaluation result. Cannot determine if 'true' or 'false'."
        )