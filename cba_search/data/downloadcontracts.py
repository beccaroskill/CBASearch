import pandas as pd
import urllib.request as urlreq
from multiprocessing import Pool


def download_by_doc_id(doc_id, download_folder='DOL_Scrape/Contracts'):
    doc_url = 'https://olmsapps.dol.gov/olpdr/GetAttachmentServlet?docId={}'.format(doc_id)
    web_file = urlreq.urlopen(doc_url)
    local_file = open('{}/{}.pdf'.format(download_folder, doc_id), 'wb')
    local_file.write(web_file.read())
    web_file.close()
    local_file.close()

cba_list_file = "CBAList.csv"
cba_df = pd.read_csv(cba_list_file)
download_folder = "DOL_CBAs/Contracts"
    
def main():
    with Pool(5) as p:
        p.map(download_by_doc_id, cba_df['CBA File'])

if __name__ == "__main__":
    main() 