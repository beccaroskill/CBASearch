from pdf2image import convert_from_path
import pytesseract
import cv2
import xml.etree.ElementTree as ET
import numpy as np
from tqdm import tqdm
import os
from pathlib import Path

def get_bbox(hocr_title):
    bbox_strs = hocr_title.split(' ')[1:5]
    bbox_strs[3] = bbox_strs[3][:-1]
    bbox = [int(s) for s in bbox_strs]
    return bbox

def get_wconf(hocr_title):
    tokens = hocr_title.split(' ')
    if 'x_wconf' in tokens:
        return int(tokens[tokens.index('x_wconf') + 1])
    return 0

def pdf_to_imgs(pdf_path, out_path, out_name):
    pages = convert_from_path(pdf_path, dpi=500)
    img_paths = []
    out_path_full = os.path.join(out_path, out_name)
    for i, page in enumerate(pages):
        img_path = '{}_{}.jpg'.format(out_path_full, i)
        page.save(img_path, 'JPEG')
        img_paths += [img_path]
    return img_paths

def imgs_to_md(img_paths):
    doc_lines = []
    for img_path in tqdm(img_paths):
        img = cv2.imread(img_path)    
        # Get HOCR output
        hocr = pytesseract.image_to_pdf_or_hocr(img, extension='hocr')
        root = ET.fromstring(hocr)
        for line in root.iter():
            if 'id' in line.attrib and 'line' in line.attrib['id']:
                word_texts = []
                for word in line.iter():
                    if 'id' in word.attrib and 'word' in word.attrib['id']:
                        word_conf = get_wconf(word.attrib['title'])
                        if word_conf > 10:
                            word_texts.append(word.text)
                line_text = ' '.join(word_texts)
                if is_header(line_text):
                    doc_lines.append('### ' + line_text)
                else:
                    doc_lines.append(line_text)
    doc_text = '  \n'.join(doc_lines)
    return doc_text
                    
def is_header(text):
    begins_upper = get_count_upper(text[:15]) > 0.3 * 15
    words = [c for c in text.split()]
    is_title = sum([1 for c in words if c[0].isupper()]) > 0.5 * len(words)
    return begins_upper or is_title

def get_count_upper(text):
    count_upper = sum([1 for c in text if c.isupper()])
    return count_upper

contracts_folder = 'Contracts'
imgs_folder = 'ContractImages'
txt_folder = 'ContractText'

for file_path in os.listdir(contracts_folder): 
    img_paths = []
    file_ext = Path(file_path).suffix
    if file_ext == '.pdf':
        pdf_path = os.path.join(contracts_folder, file_path)
        contract_id = file_path[:file_path.index(file_ext)]
        if not '{}.txt'.format(contract_id) in os.listdir(txt_folder):
            print('Reading', file_path)
            img_paths += [pdf_to_imgs(pdf_path, imgs_folder, contract_id)]
            for contract_img_paths in img_paths:
                text_file_path = '{}/{}.txt'.format(txt_folder, contract_id)
                doc_text = imgs_to_md(contract_img_paths)
                with open(text_file_path, "w") as text_file:
                    n = text_file.write(doc_text)