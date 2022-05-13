import os
from pathlib import Path
import pandas as pd
import json

class ContractLine:
    
    def __init__(self, text, is_header, contract_id, line_index, is_search_result):
        self.text = text
        self.is_header = is_header
        self.contract_id = contract_id
        self.line_index = line_index
        self.is_search_result = is_search_result
        
class ContractSearchResult:
    
    def __init__(self, contract_id, contract_name, contract_industry, \
                 lines, result_line_index):
        self.contract_id = contract_id
        self.contract_name = contract_name
        self.contract_industry = contract_industry
        self.lines = lines
        self.result_line_index = result_line_index

class ContractDatabase:
    
    def __init__(self, contract_text_folder, contract_metadata_file, naics_structure_file):
        self.contract_text_folder = contract_text_folder
        self.contract_text_db = self.load_contract_text(contract_text_folder)
        self.contract_metadata_db = pd.read_csv(contract_metadata_file)
        self.naics_structure_db = pd.read_csv(naics_structure_file)
        
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
    
    def get_industries(self):
        codes = self.naics_structure_db['2022 NAICS Code']
        titles = self.naics_structure_db['2022 NAICS Title']
        industries = [{"name": "All industries", "sub_industries":[{"name": "All industries",
                                                                    "codes": "[]"}]}]
        industry=None
        for code, title in zip(codes,titles):
            code = str(code)
            if title==title:
                title = str(title)
                trim_index = title.find('T', len(title)-3, len(title))
                title_trimmed = title[:trim_index] if trim_index>0 else title
                codes = code.split('-')
                if len(codes[0])==2:
                    if industry:
                        industries.append(industry)
                    industry = {"name": title_trimmed, 
                                "sub_industries":[{"name":"All " + title_trimmed,
                                                   "codes": [int(c) for c in codes]}]}
                elif len(codes[0])==3:
                    industry["sub_industries"].append({"name": title_trimmed, 
                                                       "codes": [int(c) for c in codes]})
        return industries
    
    def get_contract_name(self, contract_id):
        id_matches = self.contract_metadata_db[self.contract_metadata_db['CBA File']==int(contract_id)]['Union']
        assert len(id_matches) > 0, \
            "Invalid value for contract_id, no contracts match in database."
        return id_matches.tolist()[0]
    
    def get_contract_link(self, contract_id):
        id_matches = self.contract_metadata_db[self.contract_metadata_db['CBA File']==int(contract_id)]
        assert len(id_matches) > 0, \
            "Invalid value for contract_id, no contracts match in database."
        return f"https://olmsapps.dol.gov/olpdr/GetAttachmentServlet?docId={contract_id}"
        
    def get_contract_sector(self, contract_id):
        id_matches = self.contract_metadata_db[self.contract_metadata_db['CBA File']==int(contract_id)]['Type']
        assert len(id_matches) > 0, \
            "Invalid value for contract_id, no contracts match in database."
        return id_matches.tolist()[0]
            
    def get_contract_industry(self, contract_id):
        id_matches = self.contract_metadata_db[self.contract_metadata_db['CBA File']==int(contract_id)]['NAICS*']
        assert len(id_matches) > 0, \
            "Invalid value for contract_id, no contracts match in database."
        return id_matches.tolist()[0]
    
    def get_contract_text(self, contract_id):
        contract_lines = self.contract_text_db[self.contract_text_db['contract_id']==str(contract_id)]
        contract_name = self.get_contract_name(contract_id)
        contract_industry = self.get_contract_industry(contract_id)
        lines = []
        for _, line_row in contract_lines.iterrows():
            line = ContractLine(line_row['text'], line_row['is_header'], line_row['contract_id'], 
                                line_row['line_index'], False)
            lines.append(line)
        search_result = ContractSearchResult(contract_id, contract_name, contract_industry, lines, 0)
        return search_result 

    def get_all_contracts(self, filters=None):
        matches = self.contract_text_db[self.contract_text_db['line_index']==0]
        if filters:
            matches = self.filter_search_results(matches, filters)
            matches = matches[:min(len(matches),40)]
        print(matches, filters)
        search_results = []
        for _, match in matches.iterrows():
            line_index = match['line_index']
            contract_id = match['contract_id']
            contract_name = self.get_contract_name(contract_id)
            contract_industry = self.get_contract_industry(contract_id)
            contract_lines = self.contract_text_db[self.contract_text_db['contract_id']==contract_id]
            line_range_min = max(0, line_index-3)
            line_range_max = min(line_index+3, len(contract_lines))
            matches_adj = contract_lines[(contract_lines['line_index']>=line_range_min) & \
                                         (contract_lines['line_index']<=line_range_max)]
            lines = []
            for _, match_adj in matches_adj.iterrows():
                line = ContractLine(match_adj['text'], match_adj['is_header'], match_adj['contract_id'], 
                                    match_adj['line_index'], False)
                lines.append(line)
            search_result = ContractSearchResult(contract_id, contract_name, contract_industry, lines, line_index)
            search_results.append(search_result)
        return search_results
    
    def filter_search_results(self, search_results, filters):
        filter_industry_codes = json.loads(filters['industry_codes'])
        valid_index = []
        for _, result in search_results.iterrows():
            valid = False
            contract_id = result['contract_id']
            contract_industry = self.get_contract_industry(contract_id)
            if len(filter_industry_codes):
                for code in filter_industry_codes:
                    code = str(code)
                    if contract_industry == contract_industry:
                        result_industry = str(int(contract_industry))
                        if result_industry[:len(code)]==code:
                            valid = True
            else:
                valid = True
            valid_index.append(valid)
        return search_results[valid_index]
    
    def get_search_results(self, search_term, filters):
        matches = self.contract_text_db[self.contract_text_db['text'].str.contains(search_term, case=False)]
        filtered_matches = self.filter_search_results(matches, filters)
        filtered_matches = filtered_matches[:min(len(filtered_matches),40)]
        search_results = []
        for _, match in filtered_matches.iterrows():
            line_index = match['line_index']
            contract_id = match['contract_id']
            contract_name = self.get_contract_name(contract_id)
            contract_industry = self.get_contract_industry(contract_id)
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
            search_result = ContractSearchResult(contract_id, contract_name, contract_industry, lines, line_index)
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
    
