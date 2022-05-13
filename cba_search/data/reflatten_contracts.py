import os
import json

structured_folder = 'DOL_Scrape/ContractText_Structured'
reflattened_folder = 'DOL_Scrape/ContractText_Reflattened'
all_headers = []

for file_path in os.listdir(structured_folder): 
    if 'json' in file_path:
        contract_text = ''
        json_path = os.path.join(structured_folder, file_path)
        with open(json_path) as json_f:
            file_structure = json.load(json_f)
            for header, body in file_structure:
                if header:
                    for line in header.split('\n'):
                        contract_text += '### ' + line + '\n'
                    for line in body.split('\n'):
                        contract_text += line + '\n'
            
        with open(os.path.join(reflattened_folder, file_path[:-5] + '.txt'), 'w') as f:
            f.write(contract_text)