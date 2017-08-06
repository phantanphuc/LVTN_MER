#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 21:30:37 2017

@author: ngocbui
"""

import numpy as np
import xml.etree.ElementTree as r
import torch
from torch.autograd import Variable
import os
import re
import collections

def readSymbolfile(path):
    assert(os.path.exists(path))
    with open(path, 'r') as f:
        return f.read().replace("\n", " ").split()
    
def buildVocab(path):
    
    data = readSymbolfile(path)
    counter = collections.Counter(data)
#    print(counter)
    count_pairs = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
#    print(count_pairs)
    words, _ = list(zip(*count_pairs))
    word_to_id = dict(zip(words, range(len(words))))
    id_to_word = dict((v, k) for k, v in word_to_id.items())
#    print(word_to_id)
#    print(id_to_word)
#    train = _file_to_word_ids(truth, word_to_id)
#    print(train)
    return word_to_id, id_to_word

def replaceW2ID(data, word_to_id):
    print('data', data)
#    data = readSymbolfile(path)
    return [word_to_id[word] for word in data if word in word_to_id]


def touchGT(path):
    assert(os.path.exists(path))
    root = r.parse(path).getroot()
    print('parse', r.parse(path))
    print(root.tag)
    #print(root.getchildren())
    tag_header_len = len(root.tag)-3
    
    for child in root:
        tag = child.tag[tag_header_len:]
#        print(tag)
        if tag == 'annotation' and child.attrib['type'] == 'truth':
            text = child.text
            print(text)
            text = text.replace('$','')
            print(text)
#            print(text.split())
#            text = text.split()
    return text


def getRoot(path):
    assert(os.path.exists(path))
    root = r.parse(path).getroot()
    return root

def modifiedText(text):
    standard = ['phi','pi','theta','alpha','beta','gamma','infty','sigma','Delta',
                'lamda','mu','pm','sin','cos','neq','leq','gt','sqrt','div','times',
                'sum','log','tan','ldots','geq','rightarrow','lim','int','exists',
                'forall','in','prime']
    if text in standard:
        standtext = '\\'+text
    else:
        standtext = text
    return standtext
def processBrac(elem, length, is_fisrt):
    parent = elem.getparent()
    parent_tag = parent.tag[length:]
    if parent_tag == 'mfrac':
        if is_first:
            text = '{'
        else:
            text = '}'
    return text
            
def parseGT(root, text, ignoreElems, length):
    
    if root.tag[length:] in ignoreElems:
        return
    if len(root) == 0:
        
            
        temp = modifiedText(root.text)
        text.append(temp)
        return
    else:
#        print(root.tag[length+6:])
        if root.tag[length+6:] == 'msqrt':
            text.append('\\sqrt')
            text.append('{')
            for child in root:
                parseGT(child, text, ignoreElems, length)
            text.append('}')
        elif root.tag[length+6:] == 'mfrac':
            text.append('\\frac')
            for child in root:
                text.append('{')
                parseGT(child, text, ignoreElems, length)
                text.append('}')  
        elif root.tag[length+6:] == 'msub':
            n = 1
            for child in root:
                if n == 2:
                    text.append('_')
                    if child.tag[length+6:] == 'mrow':
                        text.append('{')
                        parseGT(child, text, ignoreElems, length)
                        text.append('}')
                    else:
                        parseGT(child, text, ignoreElems, length)
                else:
                    parseGT(child, text, ignoreElems, length)
                n = n + 1
        elif root.tag[length+6:] == 'msup':
            n = 1
            for child in root:
                if n == 2:
                    text.append('^')
                    if child.tag[length+6:] == 'mrow':
                        text.append('{')
                        parseGT(child, text, ignoreElems, length)
                        text.append('}')
                    else:
                        parseGT(child, text, ignoreElems, length)
                else:
                    parseGT(child, text, ignoreElems, length)
                n = n + 1
        elif root.tag[length+6:] == 'msubsup':
            n = 1
            for child in root:
                if n == 2:
                    text.append('_')
                    if child.tag[length+6:] == 'mrow':
                        text.append('{')
                        parseGT(child, text, ignoreElems, length)
                        text.append('}')
                    else:
                        parseGT(child, text, ignoreElems, length)
                elif n == 3:
                    text.append('^')
                    if child.tag[length+6:] == 'mrow':
                        text.append('{')
                        parseGT(child, text, ignoreElems, length)
                        text.append('}')
                    else:
                        parseGT(child, text, ignoreElems, length)
                else:
                    parseGT(child, text, ignoreElems, length)
                n = n + 1
                    
        else:
            for child in root:
                parseGT(child, text, ignoreElems, length)
           
def makeOneshotGT(path_to_ink, path_to_symbol):
    word_to_id, id_to_word = buildVocab(path_to_symbol)
#    chuan hoa text de tach ra duoc tung symbol va luu thanh mang trong data
#    TODO
#    data = ['\\forall', 'g', '\\in', 'G'] 
    print(touchGT(path_to_ink))
    root = getRoot(path_to_ink)
    length = len(root.tag) -3
    ignoreElems = ['traceFormat','annotation','trace','traceGroup']
    text = []
    parseGT(root, text, ignoreElems, length)
    print ('gt', text)
    vector = replaceW2ID(text, word_to_id)
    print('vector', vector)
    tensor = torch.LongTensor(vector)
    print('vector',Variable(tensor))
    return Variable(tensor)

##   tach symbol             
#def oneshotGT(path_to_ink, path_to_symbol):
#    symbols = readSymbolfile(path_to_symbol)
#    print(symbols)
#    #print(symbols.split())
#    text = touchGT(path_to_ink).split()
#    print(text)
#    truth = []
##    keyword = '[^\\\\]+(\\\\[a-zA-Z]+)+ | [^\\\\]*(\\\\[a-zA-Z]+)(\\\\[a-zA-Z]+)+'
#    keyword1 = '[^\\\\]*(\\\\[a-zA-Z]+)(\\\\[a-zA-Z]+)'
#    keyword2 = '[^\\\\]+(\\\\[a-zA-Z]+)+'
##    keyword = '[^i]+'
##    print(keyword)
#    for word in text:
#        
#        if re.match(keyword1, word, re.I) or re.match(keyword2, word, re.I):
#            print('tttrue')
##            print(re.match(keyword, word, re.I).group())
##            print(word)
#            word = word.split('\\')
#            truth.extend(word)
#            wordtoid = buildVocab(path_to_symbol)
#            truth = ['\\forall', 'g', '\\in', 'G']
#            
#            print(wordtoid)
#            xyz = _file_to_word_ids(truth, wordtoid)
#            print(xyz)
#        else: 
#            truth.append(word)
##            print(truth)
#        
    
    
   
#makeOneshotGT('./101_alfonso.inkml', './mathsymbolclass.txt')
#makeOneshotGT('./8_em_65.inkml', './mathsymbolclass.txt')
#makeOneshotGT('formulaire004-equation024.inkml','./mathsymbolclass.txt')
#makeOneshotGT('./KME1G3_0_sub_21.inkml', './mathsymbolclass.txt')
makeOneshotGT('./200922-947-1.inkml', './mathsymbolclass.txt')
#buildVocab('./mathsymbolclass.txt')
#makeOneshotGT('./MfrDB0041.inkml', './mathsymbolclass.txt')
#getMathtag('./65_alfonso.inkml')