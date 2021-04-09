import os, csv
from PIL import Image
import pytesseract

# mexer somente aqui -----------------------------
config_path = 'configuration-files/config.csv'
results_dir = 'results'
dataset_dir = 'dataset'
tessdata = 'tessdata4'
# ------------------------------------------------

def load_configs(config_path):
    configs = []
    with open(config_path, mode='r') as config_box:
        reader = csv.reader(config_box)
        for row in reader:
            configs.append({'id': row[0], 'desc': row[1]})
    return configs

def generate_tesseract_hocr(path, results_dir, config_path, engine='tessdata4'):
    configs = load_configs(config_path)
    print('\nGenerating HOCR...')
    print('File: %s' % path)
    img = Image.open(path)
    for config in configs:
        print('Config: %s' % config['id'])
        filename = magic_filesystem(path, results_dir, engine, config['id'])
        print('->', filename)
        if not os.path.exists(filename):
            hocr = pytesseract.image_to_pdf_or_hocr(
                img, lang='por+eng', extension='hocr', config=config['desc'])
            f = open(filename, 'w+')
            f.write(hocr.decode('UTF-8'))
            f.close()
    print('Done!\n')

def magic_filesystem(path, results_dir, engine, config):
    path = path.split('/')
    original_filename = path[-1].split('.')

    original_filename = original_filename[0]
    new_path = '{:s}/{:s}'.format(results_dir, path[-2])
    if not os.path.exists(new_path):
        os.mkdir(new_path)
    
    filename = '{:s}/{:s}_{:s}_config{:s}.xml'.format(new_path, original_filename, engine, config)
    return filename

def generate_hocr(path, results_dir, config_path, tessdata):
    if not os.path.exists(results_dir):
        os.mkdir(results_dir)
    
    for directory in os.listdir(path): 
        if os.path.isdir(os.path.join(path, directory)):
            dir_path = os.path.join(path, directory)
            for doc in os.listdir(dir_path):
                if os.path.isfile(os.path.join(dir_path, doc)): 
                    doc_path = os.path.join(dir_path, doc)
                    generate_tesseract_hocr(doc_path, results_dir, config_path, tessdata)

if __name__ == '__main__':
    generate_hocr(dataset_dir, results_dir, config_path, tessdata)
