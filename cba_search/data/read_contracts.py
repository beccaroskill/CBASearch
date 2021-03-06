import pandas as pd
import urllib.request as urlreq
from multiprocessing import Pool
import pytesseract
from pdf2image import convert_from_path, pdfinfo_from_path
import cv2
import xml.etree.ElementTree as ET
import os
from pathlib import Path

contracts_folder = 'DOL_Scrape/Contracts'
imgs_folder = 'DOL_Scrape/ContractImages'
txt_folder = 'DOL_Scrape/ContractText'
cba_list_file = "CBAList.csv"
cba_df = pd.read_csv(cba_list_file)
download_folder = "DOL_CBAs/Contracts"

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
    info = pdfinfo_from_path(pdf_path)
    pages = info['Pages']
    page_block_size = 100
    n_full_groups = pages//page_block_size
    page_ranges = [(i*page_block_size, (i+1)*page_block_size-1) for i in range(n_full_groups)] + \
                  [(page_block_size*n_full_groups, pages)]
    img_paths = []
    for j, (first_page, last_page) in enumerate(page_ranges):
      pages = convert_from_path(pdf_path, dpi=500, first_page=first_page, last_page=last_page)
      out_path_full = os.path.join(out_path, out_name)
      for i, page in enumerate(pages):
          img_path = '{}_{}.jpg'.format(out_path_full, i+page_block_size*j)
          page.save(img_path, 'JPEG')
          img_paths.append(img_path)
    return img_paths

def imgs_to_md(img_paths):
    doc_lines = []
    for img_path in img_paths:
        img = cv2.imread(img_path)    
        # Get HOCR output
        hocr = pytesseract.image_to_pdf_or_hocr(img, extension='hocr')
        root = ET.fromstring(hocr)
        prev_line_article_header = False
        for line in root.iter():
            if 'id' in line.attrib and 'line' in line.attrib['id']:
                word_texts = []
                for word in line.iter():
                    if 'id' in word.attrib and 'word' in word.attrib['id']:
                        word_conf = get_wconf(word.attrib['title'])
                        if word_conf > 10:
                            word_texts.append(word.text)
                line_text = ' '.join(word_texts)
                if is_header(line_text, prev_line_article_header):
                    doc_lines.append('### ' + line_text)
                else:
                    doc_lines.append(line_text)
                prev_line_article_header = is_article_header(line_text)
    doc_text = '  \n'.join(doc_lines)
    return doc_text

def is_header(text, prev_line_article_header=False):
    is_upper = get_count_upper(text) > 0.5 * len(text)
    words = [c for c in text.split()]
    is_article_title = prev_line_article_header and sum([1 for c in words if c[0].isupper()]) > 0.5 * len(words)
    return is_upper or is_article_title

def is_article_header(text):
    words = [c for c in text.split()]
    words_lower = [c.lower() for c in words]
    is_article_header = ('article' in words_lower)
    return is_article_header

def get_count_upper(text):
    count_upper = sum([1 for c in text if c.isupper()])
    return count_upper

def read_contract_from_path(file_path):
    file_ext = Path(file_path).suffix
    if file_ext == '.pdf':
        try:
            pdf_path = os.path.join(contracts_folder, file_path)
            contract_id = file_path[:file_path.index(file_ext)]
            if not '{}.txt'.format(contract_id) in os.listdir(txt_folder):
                print('Reading', file_path)
                img_paths = pdf_to_imgs(pdf_path, imgs_folder, contract_id)
                text_file_path = '{}/{}.txt'.format(txt_folder, contract_id)
                doc_text = imgs_to_md(img_paths)
                with open(text_file_path, "w") as text_file:
                    text_file.write(doc_text)
                for img_path in img_paths:
                    os.remove(img_path)
                os.remove(pdf_path)
        except Exception as e:
            print(e)


def download_by_doc_id(doc_id, download_folder='DOL_Scrape/Contracts'):
    doc_url = 'https://olmsapps.dol.gov/olpdr/GetAttachmentServlet?docId={}'.format(doc_id)
    web_file = urlreq.urlopen(doc_url)
    local_file = open('{}/{}.pdf'.format(download_folder, doc_id), 'wb')
    local_file.write(web_file.read())
    web_file.close()
    local_file.close()
    
def main():
    block_size = 128
    pool_size = 14
    with Pool(pool_size) as p:
        all_file_ids = [f_id for f_id in cba_df['CBA File'] if not f'{f_id}.txt' in os.listdir(txt_folder)]
        split_list = lambda l, x: [l[i:i+x] for i in range(0, len(l), x)]
        file_id_blocks = split_list(all_file_ids, block_size)
        for i, file_id_block in enumerate(file_id_blocks):
            print('Downloading', (i+1), 'of', len(file_id_blocks))
            p.map(download_by_doc_id, file_id_block)
            print('Reading', (i+1), 'of', len(file_id_blocks))
            p.map(read_contract_from_path, list(os.listdir(contracts_folder)))
            for f in os.listdir(imgs_folder):
                os.remove(os.path.join(imgs_folder, f))
            for f in os.listdir(contracts_folder):
                os.remove(os.path.join(contracts_folder, f))

if __name__ == "__main__":
    main() 
