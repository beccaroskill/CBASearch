import os
from pathlib import Path
import pandas as pd

class ContractLine:
    
    def __init__(self, text, is_header, contract_id, line_index, is_search_result):
        self.text = text
        self.is_header = is_header
        self.contract_id = contract_id
        self.line_index = line_index
        self.is_search_result = is_search_result
        
class ContractSearchResult:
    
    def __init__(self, contract_name, lines, result_line_index):
        self.contract_name = contract_name
        self.lines = lines
        self.result_line_index = result_line_index

class ContractDatabase:
    
    def __init__(self, contract_text_folder, contract_metadata_file):
        self.contract_text_db = self.load_contract_text(contract_text_folder)
        self.contract_metadata_db = pd.read_csv(contract_metadata_file)
        
    def load_contract_text(self, contract_text_folder):
        lines_all = []
        for file_path_str in os.listdir(contract_text_folder): 
            file_path = Path(file_path_str)
            file_ext = file_path.suffix
            if file_ext == '.txt':
                contract_id = file_path.stem
                lines_contract = ContractDatabase.get_contract_lines(contract_text_folder, contract_id)
                lines_all += lines_contract
        df = pd.DataFrame(lines_all, columns=['text', 'is_header', 'contract_id', 'line_index'])
        return df
    
    def get_contract_name(self, contract_id):
        id_matches = self.contract_metadata_db[self.contract_metadata_db['CBA File']==int(contract_id)]['Union']
        if len(id_matches):
            return id_matches.tolist()[0]
        else:
            return "???"
    
    def get_search_results(self, search_term):
        matches = self.contract_text_db[self.contract_text_db['text'].str.contains(search_term, case=False)]
        search_results = []
        for _, match in matches.iterrows():
            line_index = match['line_index']
            contract_id = match['contract_id']
            contract_name = self.get_contract_name(contract_id)
            contract_lines = self.contract_text_db[self.contract_text_db['contract_id']==contract_id]
            line_range_min = max(0, line_index-3)
            line_range_max = min(line_index+3, len(contract_lines))
            matches_adj = contract_lines[(contract_lines['line_index']>=line_range_min) & \
                                         (contract_lines['line_index']<=line_range_max)]
            lines = []
            for _, match_adj in matches_adj.iterrows():
                line = ContractLine(match_adj['text'], match_adj['is_header'], match_adj['contract_id'], 
                                    match_adj['line_index'], match_adj['line_index']==line_index)
                lines.append(line)
            search_result = ContractSearchResult(contract_name, lines, line_index)
            search_results.append(search_result)
        return search_results
        
    def lines_to_response(lines, contract_id):
        response = []
        for line_index, line in enumerate(lines):
            if line[:3]=='###':
                response.append([line[4:], True, contract_id, line_index])
            else:
                response.append([line, False, contract_id, line_index])
        return response
    
    def get_contract_lines(contract_text_folder, contract_id):
        with open(f'{contract_text_folder}/{contract_id}.txt') as f:
            lines = f.readlines()
        return ContractDatabase.lines_to_response(lines, contract_id)
    
