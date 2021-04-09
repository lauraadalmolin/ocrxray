import numpy as np
import fitz
from lxml import etree, html

def warp_perspective(hocr,H):
    # Transforma a geometria das bounding boxes do hocr de acordo com a matriz de homografia H
    import numpy
    import re

    # Expressão regular para extrair bounding box de elementos
    re_bbox = re.compile(r'(?<=bbox )(\d+) (\d+) (\d+) (\d+)')    

    # Percorre todos elementos que tem bounding box
    doc=etree.fromstring(hocr)
    for element in doc.iter():
        eclass = element.get("class")
        if eclass == 'ocr_page':
            continue

        title = element.get("title")
        if title is not None:
            bbox_str=re_bbox.search(title)
            if bbox_str is not None:
                # Se tem bbox, extrai e transforma
                bbox = bbox_str.group(0).split(' ')
                bboxf = [float(x) for x in bbox]
                p1 = bboxf[0:2]
                p2 = bboxf[2:4]

                # Transforma pontos usando homografia
                p1.append(1)
                p2.append(1)
                m1 = numpy.matmul(H,p1)
                m2 = numpy.matmul(H,p2)
                mf1 = numpy.divide(m1,m1[2])
                mf2 = numpy.divide(m2,m2[2])
                p1t = mf1.astype(int)
                p2t = mf2.astype(int)


                # Atualiza title do hocr
                element.set("title",'bbox ' + str(p1t[0]) + ' ' + str(p1t[1]) + ' ' + str(p2t[0]) + ' ' + str(p2t[1]))

    doc2 = etree.tostring(doc)
    return doc2

def correct_skew(doc, angle):
    hocr_file = open(doc, 'rb')
    hocr = hocr_file.read()
    hocr_file.close()

    radians = np.radians(angle)

    homography_matrix = np.array([[np.cos(radians), - np.sin(radians), 0],
                                [np.sin(radians), np.cos(radians), 0],
                                [0, 0, 1]])
    Hinv = np.linalg.inv(homography_matrix)
    new_hocr = open('test.xml', 'wb+')
    new_hocr.write(warp_perspective(hocr, Hinv))


correct_skew('original.xml', 1)


