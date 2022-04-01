import os

contracts_folder = 'data/DOL_Scrape/ContractText'

def lines_to_response(lines):
    response = []
    for line in lines:
        if line[:3]=='###':
            response.append({'text': line[4:], 'is_header': True})
        else:
            response.append({'text': line, 'is_header': False})
    return response

def get_contract_lines(contract_id):
    contract_text_file = f'{contracts_folder}/{contract_id}.txt'
    if os.path.exists(contract_text_file):
        with open(contract_text_file) as f:
            lines = f.readlines()
        return lines_to_response(lines)
    return ''