# -*- coding: utf-8 -*-
# Mexer somente aqui ---------------------------

output_path = 'processed-metrics'
charts = 'charts'
configs = 'configuration-files/config.csv'

# ----------------------------------------------
import re
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os, csv
import numpy as np

def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split(r'(\d+)', text)]

''' 
recebe uma string com o tipo de métrica (accsum ou wordaccsum)
retorna um dicionário com base no parâmetro:
    [
        {
            'name': 'portrait', # nome do dataset
            'values': [
                {
                    'xName': 'tessdata4_config1', # configuração
                    'yValue': 21.1 # percentual de acurácia relativo ao parâmetro
                }
            ]
        }, 
        ...
    ]
'''
def __process_data(output_path, chart_type: str):

    chart_data = []
    full_path = os.path.join(output_path, chart_type)
    for doc_path in os.listdir(full_path):

        full_doc_path = os.path.join(full_path, doc_path)

        splitted_doc_name = doc_path.split('-tess')
        dataset_name = splitted_doc_name[0]
        xName = 'tess' + splitted_doc_name[1].replace('.txt', '')
        
        doc = open(full_doc_path)
        yValue = doc.readlines()[4]
        yValue = yValue.split('%')[0].strip()
        yValue = float(yValue)
        doc.close()

        index = -1
        for i, data in enumerate(chart_data):
            if data['name'] == dataset_name:
                index = i

        if index == -1:
            chart_data.append({
                'name': dataset_name,
                'values': [
                    {
                        'xName': xName,
                        'yValue': yValue
                    }
                ]
            })
        else:
            chart_data[index]['values'].append({
                'xName': xName,
                'yValue': yValue
            })

    return chart_data

def plot_charts(output_path, chart_type: str):
    charts_data = __process_data(output_path, chart_type)
    for data in charts_data:
        xSeries = []
        xLabel = []
        ySeries = []

        for i, value in enumerate(data['values']):
            xLabel.append(value['xName'])
            xSeries.append(i + 4)
            ySeries.append(value['yValue'])

        axes = plt.gca()
        axes.set_ylim([0, 100])
        plt.bar(xSeries, ySeries, align='center', )
        plt.title(data['name'])
        plt.xticks(xSeries, xLabel, rotation='45', ha='right')
        for p in axes.patches:
            width = p.get_width()
            height = p.get_height()
            x, y = p.get_xy()
            axes.annotate(f'{height}%', (x + width/2, y + height*1.2), ha='center')
        plt.legend()
        plt.tight_layout()

        plt.savefig(charts + '/' + chart_type + '-' + data['name'] + '.jpeg')
        plt.close()

# gera uma matriz baseada em um token que deve estar presente 
# nos arquivos do dataset
# dado um token=portrait, serão procurados todos os resultados 
# contendo 'portrait' e será plotada a matriz
def process_matrix(output_path, token: str, title: str, output_name: str, metrics_type='acc'):

    if metrics_type == 'acc':
        metrics_type = 'accsum'
    elif metrics_type == 'wordacc':
        metrics_type = 'wordaccsum'


    charts_data = __process_data(output_path, metrics_type)
    subdatasets = []
    configs = []

    for i, data in enumerate(charts_data):
        if (token in data['name']):
            subdatasets.append(data['name'])
        if (i == 0):
            for value in data['values']:
                configs.append(value['xName'])

    subdatasets.sort(key=natural_keys)
    configs.sort(key=natural_keys)

    config_ticks = []
    for i, _ in enumerate(configs):
        config_ticks.append('L{:d}'.format(i+1))
    
    __plot_matrix(subdatasets, configs, config_ticks,
                  charts_data, title, output_name, output_path)

def __get_legends():
    legends = []
    with open(configs, mode='r') as config_box:
        reader = csv.reader(config_box)
        for row in reader:
            legends.append(row[0] + ': ' + row[1])
    return legends

def __plot_matrix(subdatasets, configs, config_ticks, charts_data, title, output_name, output_path=''):
    percents = []

    for dataset in subdatasets:
        dataset_values = []
        for i, data in enumerate(charts_data):
            if data['name'] == dataset:
                for config in configs:
                    for value in data['values']:
                        if (config == value['xName']):
                            dataset_values.append(value['yValue'])
        percents.append(dataset_values)
    percents = np.array(percents)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(percents)

    # We want to show all ticks...
    ax.set_xticks(np.arange(len(config_ticks)))
    ax.set_yticks(np.arange(len(subdatasets)))
    # ... and label them with the respective list entries
    ax.set_xticklabels(config_ticks)
    ax.set_yticklabels(subdatasets)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
            rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(subdatasets)):
        for j in range(len(configs)):
            ax.text(j, i, percents[i, j], fontsize=10,
                           ha="center", va="center", color="w")

    legends = __get_legends()
    ax.legend(legends)
    ax.set_title(title)
    fig.tight_layout()

    if output_path == '':
        output_path = 'charts'
    else:
        output_path += '/charts'

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    plt.savefig(output_path + '/' + output_name + '.jpeg', dpi=200)
    plt.close()


if __name__ == '__main__':
    # plot_charts('accsum')
    # plot_charts('wordaccsum')
    process_matrix(output_path, 'landscape', 'Acurácia (0-100) | Orientação Paisagem', 'landscape_accuracy', 'acc')
    process_matrix(output_path, 'portrait', 'Acurácia (0-100) | Orientação Retrato', 'portrait_accuracy', 'acc')
    process_matrix(output_path, 'landscape', 'Acurácia por Palavra (0-100) | Orientação Paisagem', 'landscape_word_accuracy', 'wordacc')
    process_matrix(output_path, 'portrait', 'Acurácia por Palavra (0-100) | Orientação Retrato', 'portrait_word_accuracy', 'wordacc')
