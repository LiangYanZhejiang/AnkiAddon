#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import socket
import requests
import logging
from anki_common import Anki_common
from WordDownLoad import do_request
from DownLoadThread import threadManager

def import_words(words):
    socket.setdefaulttimeout(5)

    existsWords = set()
    Import_path = Anki_common().import_dir()
    if os.path.exists(Import_path):
        for filename in os.listdir(Import_path):
            if (os.path.isdir(Import_path + '\\' + filename)):
                existsWords.add(filename)
    else:
        os.mkdir(Import_path)

    # 去除重复单词
    #words = list(set(words) - existsWords)
    threadManager(list(set(words)),list(existsWords))


def main():
    if not os.path.exists(Anki_common().words_path()):
        tips = "Please give your wordlist in folder: %s." % Anki_common.words_path()
        logging.error(tips)

    words = []
    words_path = Anki_common().words_path()
    for filename in os.listdir(words_path):
        if (os.path.isdir(words_path + '\\' + filename)):
            continue;
        f = open(words_path + '\\' + filename, 'r')

        # 将单词字母小写
        for word in f.readlines():
            word = unicode(word, 'utf-8')
            words.append(word.strip('\n').lower())
        f.close()

    import_words(words)
    return

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding("utf-8")

    Anki_common(False)

    if not os.path.exists(Anki_common().log_folder()):
        os.mkdir(Anki_common().log_folder())

    log_format = '[%(asctime)s] [%(levelname)s] [%(filename)s] [%(module)s] [%(funcName)s] %(message)s'
    logging.basicConfig(format=log_format,filename=Anki_common().log_file(), filemode='a',level=logging.DEBUG)

    #console = logging.StreamHandler()
    #console.setLevel(logging.DEBUG)
    #console.setFormatter(log_format)
    #logging.getLogger('').addHandler(console)

    main()