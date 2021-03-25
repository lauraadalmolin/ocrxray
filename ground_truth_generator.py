import os, sys, argparse, fitz
sys.path.append('utils')
from hocr_from_searchable import  is_searchable, create_hocr_from_searchable, combine_hocr

input_path = 'pdfs/'
output_path = 'ground-truth/'

if (os.path.isdir(input_path)):

    for filename in os.listdir(input_path):

        hocr_list = []
        doc = fitz.open(input_path+filename)
        
        for page_number,page in enumerate(doc):
            hocr = create_hocr_from_searchable(page, page_number)
            hocr_list.append(hocr)

        hocr_final = combine_hocr(hocr_list)
        filename = filename.replace(".pdf", "")

        with open(output_path+filename+".xml","w+") as f:
            f.write(hocr_final.decode('UTF-8'))
            f.close()
            