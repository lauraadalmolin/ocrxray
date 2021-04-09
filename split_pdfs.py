import fitz
import os
def split_pdfs(pdfs_dir, output_path):
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    for pdf_name in os.listdir(pdfs_dir):
        pdf_path = os.path.join(pdfs_dir, pdf_name)

        if os.path.isfile(pdf_path):
            doc = fitz.open(pdf_path)

            for page_i, _ in enumerate(doc):
                output = output_path + '/' + pdf_name[:-4] + '_page' + str(page_i) + '.pdf'
                # Cria novo pdf para a unica pagina
                pdf_page = fitz.open()
                # Insere a pagina no pdf
                pdf_page.insertPDF(doc, from_page=page_i, to_page=page_i)
                # Salva o pdf splittado
                pdf_page.save(output)
                # Fecha o arquivo
                pdf_page.close()
