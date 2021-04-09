# -*- coding: utf-8 -*-
# Mexer somente aqui ---------------------------
input_folder =  'raw-pdf'
dataset_variations = 0
config_path = 'configuration-files/config2.csv'
tessdata = 'tessdata4'

chart_title = ''
# ----------------------------------------------
root = input_folder + '-processed'
pdf = root + '/pdf'
dataset = root + '/dataset'
original_dataset_name = 'original'
full_dataset_path = dataset + '/' + original_dataset_name
ground_truth = root + '/ground-truth'
hocr = root + '/hocr'
metrics = root + '/metrics'
results = root + '/results'

import shutil, csv, os
from split_pdfs import split_pdfs
from generate_ground_truths import generate_ground_truths
from generate_dataset import generate_dataset
from generate_hocr import generate_hocr
from generate_txt import generate_txt
from generate_metrics import generate_metrics, sum_metrics
from plot_charts import process_matrix
from generate_images import generate_images

if not os.path.exists(root):
    os.mkdir(root)

# configs = get config names 
configs = []
with open(config_path, mode='r') as config_box:
    reader = csv.reader(config_box)
    for row in reader:
        configs.append('config' + row[0])

print('Fazendo split dos pdfs...')
split_pdfs(input_folder, pdf)

print('Gerando ground-truths...')
generate_ground_truths(pdf, ground_truth)

print('Gerando imagens...')
generate_images(pdf, dataset, original_dataset_name) # implementar

# remova essa linha se você quer ter acesso aos pdfs de página única
print('Removendo pdfs de página única para poupar espaço em disco...')
shutil.rmtree(pdf)

print('Gerando o dataset com {:d} variações...'.format(dataset_variations))
generate_dataset(full_dataset_path, dataset_variations)

print('Fazendo OCR...')
generate_hocr(dataset, hocr, config_path, tessdata)

print('Convertendo para txt...')
generate_txt(ground_truth, hocr, metrics)

print('Calculando as métricas por arquivo...')
generate_metrics(metrics)

print('Processando arquivos...')
sum_metrics(metrics, configs, results)

process_matrix(results, original_dataset_name, 'Acurácia (0-100)', 'original_accuracy', 'acc')
process_matrix(results, original_dataset_name, 'Acurácia por Palavra (0-100)', 'original_word_accuracy', 'wordacc')

