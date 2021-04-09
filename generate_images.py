import os
from pdf2image import convert_from_path

def generate_images(pdfs_dir, output_path, original_dataset_name):
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    
    output_path = os.path.join(output_path, original_dataset_name)
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    for pdf_name in os.listdir(pdfs_dir):
        pdf_path = os.path.join(pdfs_dir, pdf_name)
        output_image = os.path.join(output_path, pdf_name[:-4] + ".png")

        if not os.path.exists(output_image) and os.path.isfile(pdf_path):
            image = convert_from_path(pdf_path, dpi=300,
                                    last_page=1, first_page=0, grayscale='true', fmt='png')
            image[0].save(output_image, 'png')
