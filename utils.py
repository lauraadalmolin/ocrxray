import fitz
import csv
import sys
import pytesseract
import os
import argparse
import xml.etree.ElementTree as ET
from tempfile import mkstemp
from shutil import move, copymode
from PIL import Image
from pdf2image import convert_from_path

config_path = "configuration_files/config.csv"
results_dir = "results"

def load_configs():
    configs = []
    with open(config_path, mode='r') as config_box:
        reader = csv.reader(config_box)
        for row in reader:
            configs.append({"id": row[0], "desc": row[1]})
    return configs


def split_pdf(doc, page, output):
    # Cria novo pdf para a unica pagina
    pdf_page = fitz.open()
    # Insere a pagina no pdf
    pdf_page.insertPDF(doc, from_page=page, to_page=page)
    # Salva o pdf splittado
    pdf_page.save(output)
    # Fecha o arquivo
    pdf_page.close()


def clean_dir(outputpath, filename, clean_pdf):
    test = os.listdir(outputpath)
    for item in test:
        if not "page" in item:
            os.remove(os.path.join(outputpath, item))
        if item.endswith(".pdf") and clean_pdf is True:
            os.remove(os.path.join(outputpath, item))


def pdf_to_image(path, outputpath):
    image = convert_from_path(path, dpi=300, output_folder=outputpath,
                              last_page=1, first_page=0, grayscale='true', fmt='png')
    image[0].save(os.path.join(outputpath, path[:-4] + ".png"), 'png')


def generate_tesseract_hocr(path, engine="tessdata4"):
    configs = load_configs()
    print("Generating HOCR...")
    print("File:   %s" % path)
    img = Image.open(path)
    for config in configs:
        print("Config:   %s" % config["desc"])
        filename = magic_filesystem(path, engine, config["id"])
        print('-> ', filename)
        if not os.path.exists(filename):
            hocr = pytesseract.image_to_pdf_or_hocr(
                img, lang='por', extension="hocr", config=config["desc"])
            f = open(filename, "w+")
            f.write(hocr.decode('UTF-8'))
            f.close()
    print("Done!")


def generate_gvision_hocr(path, engine="gvision"):
    print("Generating HOCR...")
    print("File:   %s" % path)
    img = Image.open(path)
    print('here')
    filename = magic_filesystem(path, engine)
    if not os.path.exists(filename):
        hocr = OcrGoogle(img)
        f = open(filename, "w+")
        f.write(hocr.decode('UTF-8'))
        f.close()
    print("Done!")


def magic_filesystem(path, engine, psm):
    path = path.split('/')
    original_filename = path[2].split('.')

    extension = original_filename[1]
    original_filename = original_filename[0]

    new_path = "{:s}/{:s}".format(results_dir, path[1])

    if not os.path.exists(new_path):
        os.mkdir(new_path)
    
    filename = "{:s}/{:s}_{:s}_psm{:s}.{:s}".format(new_path, original_filename, engine, psm, extension)

    return filename


def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def preprocess_filename(path):
    path = path.split('_png.')
    return path[0]


def convert_jpg_to_png(path):
    if path.endswith(".png"):
        return
    else:
        if path.endswith(".jpg"):
            print("Converting....")
            print("File: " + path)
            img = Image.open(path)
            png_path = preprocess_filename(path)
            img.save(png_path + ".png")
            print("Done!")
            os.remove(path)


def clean_hocr(hocr):
    pages = hocr.findall(".//*[@class='ocr_page']")
    for page in pages:
        areas = page.findall(".//*[@class='ocr_carea']")
        for area in areas:
            pars = area.findall(".//*[@class='ocr_par']")
            for par in pars:
                lines = (par.findall(".//*[@class='ocr_line']") +
                         par.findall(".//*[@class='ocr_textfloat']") +
                         par.findall(".//*[@class='ocr_caption']") +
                         par.findall(".//*[@class='ocr_header']"))
                for line in lines:
                    words = line.findall(".//*[@class='ocrx_word']")
                    for word in words:
                        # palavra vazia, remove
                        if word.text is not None:
                            word.text = word.text.strip()
                        if word.text is None or word.text == '':
                            print(word.attrib['id'])
                            line.remove(word)
                    if len(line) == 0:
                        par.remove(line)
                if len(par) == 0:
                    area.remove(par)
            if len(area) == 0:
                page.remove(area)
        if len(page) == 0:
            pass  # não remove página

    return hocr


def xml_cleaner(path):
    if path.endswith(".xml"):
        remove_unused_tags(path)

        xml_tree = ET.parse(path)
        xml_root = xml_tree.getroot()

        clean_hocr(xml_root)
        xml_tree.write(path)


def remove_unused_tags(path):
    replace(path, '<strong>', '')
    replace(path, '</strong>', '')
    replace(path, '<em>', '')
    replace(path, '</em>', '')
    replace(path, ' >', '>')
    replace(path, '< ', '< ')


def replace(path, pattern, subst):
    fh, abs_path = mkstemp()
    with os.fdopen(fh, 'w') as new_file:
        with open(path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    copymode(path, abs_path)
    os.remove(path)
    move(abs_path, path)


def bb_intersection_over_union(boxA, boxB):

    if (boxA[1] > boxA[3]):
        y = boxA[3]
        boxA[3] = boxA[1]
        boxA[1] = y
    if (boxB[1] > boxB[3]):
        y = boxB[3]
        boxB[3] = boxB[1]
        boxB[1] = y

	# determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    # compute the area of intersection rectangle
    interArea = abs(max((xB - xA, 0)) * max((yB - yA), 0))
    if interArea == 0:
        return 0
    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = abs((boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    boxBArea = abs((boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)

    # return the intersection over union value
    return iou


def format_bb(standard_bb):
    array = standard_bb.split()
    new_array = [int(array[1]), int(array[2]), int(
        array[3]), int(array[4].replace(';', ''))]
    return new_array


if __name__ == "__main__":
    # find_images('/home/laura/Documents/tot/tot-ocr/tester/roboflow_dataset/', convert_jpg_to_png)
    # remove_unused_tags(
    #     '/home/laura/Workspace/ocr-tester/roboflow_dataset/landscape/32_page2/32_page2_enginetessdata5_config2.xml')
    print(bb_intersection_over_union(
        [3038, 324, 3118, 359], [3039, 332, 3117, 360]))
