import re
from itertools import count

class dataCleaner():

    def clean():
        pass

class basicDataCleaner(dataCleaner):

    def clean(self, inputfile: str, outputfile:str):

        search_html_md = "<.[^>]*>"

        with open (inputfile, 'r' ) as f:  #'data/scratch/ISTRUZIONE_OPERATIVA_CREAZIONE_VM_CLOUD_INSIEL_REV_00-with-image-refs.html'
            
            content = f.read()

            button_number_count = 0;
            
            counter_figures = count(button_number_count)
            counter_tables = count(button_number_count)

            #place placeholders instead of tables/figures
            content = re.sub(r'<figure>.*</figure>', lambda x: x.group(0) + "$$figure" + str(next(counter_figures)), content )
            content = re.sub(r'<table>', lambda x: x.group(0) + "$$table" + str(next(counter_tables)) + " <table>", content )

            #replace header
            #content = re.sub("<head>([.*\n].*)*<\\head>", "", content, re.M)

            #replace html markdown
            content = re.sub(search_html_md, " ", content, flags = re.M)

            #replace multiple dot occurrences (ex. ".....")
            content = re.sub("\.(?=\.)", "", content)
            
            content = re.sub(" IO_XX_00_XX \n", "", content)
            content = re.sub(" Creazione VM su Cloud INSIEL \n", "", content)
            content = re.sub(" ISTRUZIONE OPERATIVA \n", "", content)

        with open (outputfile, 'w' ) as f:  #'data/scratch/ISTRUZIONE_OPERATIVA_CREAZIONE_VM_CLOUD_INSIEL_REV_00-with-image-refs_cleaned.txt'
            f.write(content)