import pandas as pd
import urllib.request as urlreq
from tqdm import tqdm

def download_by_doc_id(doc_id, download_folder=''):
    doc_url = 'https://olmsapps.dol.gov/olpdr/GetAttachmentServlet?docId={}'.format(doc_id)
    web_file = urlreq.urlopen(doc_url)
    local_file = open('{}/{}.pdf'.format(download_folder, doc_id), 'wb')
    local_file.write(web_file.read())
    web_file.close()
    local_file.close()

cba_list_file = "CBAList.csv"
cba_df = pd.read_csv(cba_list_file)
download_folder = "DOL_CBAs/Contracts"
for doc_id in tqdm(cba_df['CBA File']):
    download_by_doc_id(doc_id, download_folder)