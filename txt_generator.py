# -*- coding: utf-8 -*-
from tempfile import mkstemp
from os import fdopen, remove
from shutil import move, copymode
import xml.etree.ElementTree as ET
import os, sys, os.path
from os import path
from html.parser import HTMLParser
from collections import namedtuple
import numpy as np
import cv2
from shutil import copyfile
from utils import format_bb, bb_intersection_over_union

def fix_alternate_letters(word):
    if word != None:
        if u'º' in word:
            word = word.replace(u'º', 'o')
        if u'ª' in word:
            word = word.replace(u'ª', 'a')
        if u'—' in word:
            word = word.replace(u'—', '-')
        word = word.lower()
    return word

# alterar: txtGenerator para que procure o ground-truth certo
def remove_empty_words(words):
    new_array = []
    for word in words:
        if not (word.text is None or word.text.strip() == ''):
            new_array.append(word)
    return new_array


def generate_files(words, accurate_words, output_txt, output_gt):
    if not os.path.exists(output_txt) and not os.path.exists(output_gt):
        output_txt = open(output_txt, 'a')
        output_gt = open(output_gt, 'a')
        not_found = []
        found_words = 0
        total_words = 0
        for accurate_word in accurate_words:
            found = False
            bb1 = format_bb(accurate_word.attrib['title'])
            for word in words:
                bb2 = format_bb(word.attrib['title'])
                iou = bb_intersection_over_union(bb2, bb1)
                if (iou > 0.4):
                    found = True
                    gt_word = fix_alternate_letters(accurate_word.text)
                    w = fix_alternate_letters(word.text)
                    output_gt.write(gt_word + ' ')
                    output_txt.write(w + ' ')
                    found_words += 1
            if found == False:
                not_found.append(fix_alternate_letters(accurate_word.text))
            total_words+=1
        for nf in not_found:
            if (nf is not None):
                output_gt.write(nf + ' ')
                output_txt.write('¬' + ' ')
                found_words += 1
        output_gt.close()
        output_txt.close()
        print("Accurate words: %d | Total: %d | Found: %d | Not-found: %d"%(len(accurate_words), total_words, found_words, total_words-found_words))

def get_words(root):
    words = root.findall(".//*[@class='ocrx_word']")
    print("brute words %d"%(len(words)))
    words = remove_empty_words(words)
    print("no_empty %d"%(len(words)))
    return words


def clean_dir(path):
    if os.path.exists(path):
        for filename in os.listdir(path):
            os.remove(os.path.join(path, filename))

def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

# gera, em uma dada pasta output_path, a seguinte estrutura
# output_path/
#   landscape/
#       ground_truth/
#       txt/
# retorna também as rotas para os novos arquivos.
def txt_filesystem(path, output_path):
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    folder_name = path.split('/')[-2]
    file_name = path.split('/')[-1][:-4] + '.txt'

    output_path = os.path.join(output_path, folder_name)

    if not os.path.exists(output_path):
        os.mkdir(output_path)
        os.mkdir(output_path + '/txt')
        os.mkdir(output_path + '/ground-truth')
        print('aqui')
    
    ground_truth_filename = os.path.join(output_path, os.path.join('ground-truth', file_name))
    txt_filename = os.path.join(output_path, os.path.join('txt', file_name))
    
    return ground_truth_filename, txt_filename

def txt_generator(xml, ground_truth, output_path):
    xml_tree = ET.parse(xml)
    xml_root = xml_tree.getroot()

    ground_truth_tree = ET.parse(ground_truth)
    ground_truth_root = ground_truth_tree.getroot()

    # busca as palavras
    words = get_words(xml_root)
    accurate_words = get_words(ground_truth_root)

    output_gt, output_txt = txt_filesystem(xml, output_path)

    generate_files(words, accurate_words, output_txt, output_gt)


def generate_txt(ground_truth_path, path, output_path):
    for xml in os.listdir(ground_truth_path):

        xml_path = os.path.join(ground_truth_path, xml)
        xml = xml[:-4].strip()
        
        for directory in os.listdir(path):
            if os.path.isdir(os.path.join(path, directory)):
                path2 = os.path.join(path, directory)
                for generated_file in os.listdir(path2):
                    if xml in generated_file.strip():
                        generated_file_path = os.path.join(path2, generated_file)
                        txt_generator(generated_file_path, xml_path, output_path)


if __name__ == '__main__':
    ground_truth_path =  'ground-truth/'
    path = 'results/'
    output_path = 'metrics/'
    generate_txt(ground_truth_path, path, output_path)
