import os
import json

def add_to_header(line, header, body):
   if '###' == line[:3]:
       if 'article' in line.lower() or \
                   'article' in header.lower() and not body:
           return True
   return False

def process_section(header, body):
    if 0.5*len(body)>len(header) and len(header.split('\n'))<=5:
        check_lines = body.split('\n')[:7]
        starts_w_article_count = len([x for x in check_lines if 'article' in x[:15].lower()\
                                                                  or 'side letter' in x[:20].lower()])
        total_count = len([x for x in check_lines if x.strip()])
        if starts_w_article_count > 0.4*total_count:
            return ['', section_header+section_body]
        return [section_header, section_body]
    else:
        return ['', section_header+section_body]

txt_folder = 'DOL_Scrape/ContractText'
structured_folder = 'DOL_Scrape/ContractText_Structured'
all_headers = []

for file_path in os.listdir(txt_folder): 
    txt_path = os.path.join(txt_folder, file_path)
    file_structure = []
    section_header = ''
    section_body = ''
    with open(txt_path) as txt_f:
        lines = txt_f.readlines()
        for line in lines:
            if add_to_header(line, section_header, section_body):
                line = line[4:]
                if section_body:
                    file_structure.append(process_section(section_header, section_body))
                    section_header = ''
                    section_body = ''
                section_header += line
            else:
                if '###' == line[:3]:
                    line = line[4:]
                section_body += line
    all_headers += [h.strip() for h, _ in file_structure if h]
    with open(os.path.join(structured_folder, file_path[:-4] + '.json'), 'w') as f:
        json.dump(file_structure, f)