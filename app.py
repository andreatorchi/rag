import gradio as gr
from docling_export import export_documents
from clean_data import *
from populate_database import populate_database
from query_data import query_rag
import os, yaml

with open('conf/conf.yaml') as file:
    conf = yaml.full_load(file)

def submit_query(query):
    if not query:
        gr.Warning("Please enter a non-empty query")
        return "Please enter a non-empty query"
    try:
        response = query_rag(query)[0]
        return response
    except Exception as e:
        gr.Warning("LLM error. Please re-submit your query")
        print(e)
        return "LLM error. Please re-submit your query"



def reset_app():

    input_path = conf["data_path"]["input_path"]
    export_output_path = conf["data_path"]["export_output_path"]
    export_output_filename = conf["data_path"]["export_output_filename"]
    cleaned_output_filename  = export_output_filename.split(".")[0] + "_cleaned.txt" #"ISTRUZIONE_OPERATIVA_CREAZIONE_VM_CLOUD_INSIEL_REV_00-with-image-refs_cleaned.txt"

    export_documents(input_path, export_output_path, export_output_filename)

    cleaner = basicDataCleaner()
    cleaner.clean(os.path.join(export_output_path, export_output_filename), os.path.join(export_output_path, cleaned_output_filename))

    populate_database(input_path=export_output_path, input_filename=cleaned_output_filename, clear_db=True)

    gr.Info("App reset successfully. You can now load new PDFs")
    return "App reset successfully. You can now load new PDFs"


# custom css for different age elements
custom_css = """
// customize button
button {
    background-color: grey !important;
    font-family: Arial !important;
    font-weight: bold !important;
    color: blue !important;
}



    // customize background color and use it as "app = gr.Blocks(css=custom_css)"
    //.gradio-container {background-color: #E0F7FA}
    """
def main():
    # Define the Gradio app using Blocks for a flexible layout
    app = gr.Blocks(css=custom_css)

    with app:
        gr.Markdown('''# Query your own data
    ## Ollama RAG
    - Type your query and click on Submit Query. Once the LLM sends back a reponse, it will be displayed in the Reponse field.
    - Click on Reset App to clear/reset the RAG system and re-ingest the data
        ''')
        with gr.Row():
            with gr.Column():
                query_input = gr.Textbox(label="Enter your query here", placeholder="Type your query", lines=4)
                submit_button = gr.Button("Submit")
                
        response_output = gr.Textbox(label="Response", placeholder="Response will appear here", lines=4)
        reset_button = gr.Button("Reset App")

        submit_button.click(submit_query, inputs=query_input, outputs=response_output)
        reset_button.click(reset_app, inputs=None, outputs=response_output)



    # Run the app
    app.launch()

if __name__ == "__main__":
    main()