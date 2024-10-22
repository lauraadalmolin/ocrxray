import os

path = 'metrics'
configs = ['configL1', 'configL2', 'configL3', 'configL4', 'configL5', 'configL6']
tessdata = ['tessdata4']

def generate_metrics(path):
    for directory in os.listdir(path): 
        full_directory_path = os.path.join(path, directory)

        if os.path.isdir(full_directory_path): 

            txt_directory = os.path.join(full_directory_path, 'txt')
            results_directory = os.path.join(full_directory_path, 'results')
            
            if not os.path.exists(results_directory):
                os.mkdir(results_directory)
                os.mkdir(os.path.join(results_directory, 'accuracy'))
                os.mkdir(os.path.join(results_directory, 'wordacc'))

            for doc in os.listdir(txt_directory):

                doc_path = os.path.join(txt_directory, doc)

                if os.path.isfile(doc_path): 
                    output_file = os.path.join(results_directory, 'accuracy', doc)
                    measure('accuracy', doc_path, output_file)
                    output_file = os.path.join(results_directory, 'wordacc', doc)
                    measure('wordacc', doc_path, output_file)


def sum_metrics(path, configs, output_folder='processed-metrics'):
    for directory in os.listdir(path):
        full_directory_path = os.path.join(path, directory)

        if os.path.isdir(full_directory_path):
            results_directory = os.path.join(full_directory_path, 'results', 'accuracy')
            group_measurements(configs, results_directory, directory, output_folder)

def measure(method: str, doc_path: str, output_file: str):
    ground_truth_path = doc_path.replace('/txt/', '/ground-truth/')
    command = '{:s} {:s} {:s} {:s}'.format(method, ground_truth_path, doc_path, output_file)
    # print(command)
    os.system(command)



def group_measurements(configs, results_directory: str, directory: str, output_folder):
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    if not os.path.exists(os.path.join(output_folder, 'accsum')):
        os.mkdir(os.path.join(output_folder, 'accsum'))
        os.mkdir(os.path.join(output_folder, 'wordaccsum'))
    
    all_files = [f for f in os.listdir(results_directory) if os.path.isfile(os.path.join(results_directory, f))]

    for op in configs:
        for data in tessdata:
            command = ''
            token = data + '_' + op + '.'
            for doc in all_files:
                if token in doc:
                    command = command + os.path.join(results_directory, doc) + ' '

            accsum = 'accsum ' + command + ' > ' + output_folder + '/accsum/' + directory + '-' + token + 'txt'
            waccsum = 'wordaccsum ' + command + ' > ' + output_folder + '/wordaccsum/' + directory + '-' + token + 'txt'
            waccsum = waccsum.replace('accuracy', 'wordacc')
            os.system(accsum)
            os.system(waccsum)

if __name__ == '__main__':
    generate_metrics(path)
    sum_metrics(path, configs)
