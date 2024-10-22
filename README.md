Dependências
---------
Primeiramente você precisa instalar o Tesseract e [baixar os dados](https://github.com/tesseract-ocr/tessdata_best) para a língua que deseja. Além disso, você deve ter o Python instalado e instalar os pacotes listados no `requirements.txt`.

Além das dependências de software, você precisará de um dataset previamente organizado. A organização esperada é de uma pasta contendo todos os arquivos *pdf* de página única e outra pasta contendo os arquivos de imagem.* Assim, a organização mínima que você deve seguir para prosseguir com o fluxo esperado é:

- dataset/
  - dataset-original/    -> arquivos de imagem
- pdf/                   -> arquivos pdf de página única

##### *Caso você não tenha convertido os arquivos pdf para imagem ainda, confira o anexo ao final desse tutorial.


Instruções para processamento automático:
------------
Crie uma pasta e adicione todos os arquivos pdf nela. Os arquivos pdf devem ser pesquisáveis. 
Em seguida, basta alterar os parâmetros abaixo no arquivo `process_pdfs.py.
~~~
# Parâmetros

input_folder =  'raw-pdf' # caminho para onde estão seus arquivos
dataset_variations = 5 # número de variações de blur, inclinação e ruído que você deseja para o dataset
config_path = 'configuration-files/config.csv' # caminho para o arquivo de configuração que deve estar nos moldes do exemplo
tessdata = 'tessdata4' # versão do tesseract e conjunto de dados que você está utilizando no momento
chart_title = '' # título que você quer dar aos gráficos de resultado (pode ser algo relacionado ao dataset)

~~~
O resultado de todo o processamento pode ser encontrado em uma pasta chamada (input-folder)-processed.
Dentro dessa pasta, você pode encontrar o dataset gerado, os arquivos de ocr, métricas e resultados.

A pasta *results* é dividida em accsum, wordaccsum e charts. Dentro da pasta charts você pode encontrar os gráficos plotados. Nas demais pastas você pode encontrar os arquivos .txt gerados pelo ocreval.

Instruções para processamento manual (em etapas):
------------
### 1) Geração de dataset

Você precisa utilizar o generate_dataset.py para gerar um dataset com ruído, desfoque e inclinação. Basta setar as variáveis *path* e *variation*.

~~~
# Parâmetros

path = '' # Caminho para o dataset original 

variation = 5 # valor numérico que comanda o nível das degradações. A variação se dará sempre entre 1 e o número informado.
~~~

*O caminho deve apontar para uma pasta que contém apenas imagens.

Dadas as configurações, basta rodar `python3 generate_dataset.py`.
O *dataset* será gerado na mesma pasta raiz que o seu *dataset* original se encontra. Exemplo:

- projeto/
  - dataset-original/
  - dataset-original-blur-1/
  - dataset-original-blur-2/
  - ...
  - dataset-original-noise-1/
  - dataset-original-noise-2/
  - ...
  - dataset-original-rotation-1/
  - dataset-original-rotation-2/
  - ...
  

### 2) Geração de HOCR
Para gerar os arquivos de hocr, basta alterar os parâmetros necessários e rodar `python3 generate_hocr.py`.

~~~
# Parâmetros:

config_path = 'configuration-files/config.csv' # caminho para o arquivo de configuração

results_dir = 'results' # caminho para onde serão salvos os resultados, no mesmo sistema de arquivos que se encontra o dataset

dataset_dir = 'dataset' # caminho para o dataset atual, que deve estar dividido em subpastas

tessdata = 'tessdata4' # nome que você vai dar ao conjunto de dados sendo utilizado em /usr/share/tesseract-ocr/?/tessdata/?.traineddata

~~~

### 3) Geração do ground-truth
Para gerar os arquivos ground-truth, você deve organizar *pdfs* de uma única página para cada uma das imagens do seu dataset. Cada um desses *pdfs* deve ter o mesmo nome do respectivo arquivos de imagem. Os *pdfs* devem estar na pasta *pdfs*. Em posse dos arquivos pdf, você pode rodar `python3 generate_ground_truths.py`. Tal programa tentará extrair (caso o pdf seja pesquisável), um arquivo hocr com base no conteúdo do pdf. Caso o arquivo não contenha conteúdo pesquisável, será necessário gerar um arquivo ground-truth manualmente. Os arquivos ground-truth serão armazenados na pasta 'ground-truth'.

### 4) Geração do TXT
Dados os arquivos ground-truth e os arquivos hocr gerados, basta executar `python3 generate_txt.py` com os parâmetros abaixo:

~~~
# Parâmetros:

ground_truth_path =  'ground-truth/' # caminho para a pasta que contém os .xml ground-truth gerados acima.

path = 'results/' # caminho para onde se encontram os aquivos *hocr* gerados pelo sistema no passo 2.

output_path = 'metrics/'
~~~


### 5) Geração das métricas usando ocreval
Primeiramente, você precisa ter o [ocreval](https://github.com/eddieantonio/ocreval) instalado. Depois, basta rodar `python3 generate_metrics.py` com os parâmetros corretos.

~~~
# Parâmetros:

path = 'metrics' # caminho para a pasta que vai conter os resultados

config = ['config', 'config3', 'config4', 'config1', 'config2'] # configurações utilizadas

tessdata = ['tessdata4', 'tessdata4_best'] # conjuntos de dado utilizados (deve ser o mesmo nome que consta nos arquivos gerados, veja 'results/')

~~~ 

### 6) Geração dos gráficos
Depois de passar por todas as etapas, basta rodar `python3 plot_charts.py`. Nesse programa há duas funções, uma delas gera gráficos individuais para cada subdataset(plot_charts) e a outra gera matrizes gerais (process_matrix). 

~~~
# Parâmetros:

path = 'processed-metrics' # caminho para os arquivos de métricas

charts = 'charts' # caminho para o diretório onde serão salvos os gráficos
~~~