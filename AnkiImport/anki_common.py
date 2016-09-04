#!/usr/bin/env python
# encoding: utf-8
import time
import threading
import re

WORD_PATTERN = u'^[a-z|A-Z]*[a-z|A-Z|\s]*$'

def singleton(cls):
    instances = {}

    def _singleton(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

@singleton
class Anki_common(object):
    def __init__(self, addon):
        if addon:
            from aqt import mw
            self.root_folder = mw.pm.addonFolder() + '\\AnkiImport'
        else:
            import os
            self.root_folder = os.getcwd()

    def words_path(self):
        return self.root_folder + '\\Words'

    def download_dir(self):
        return self.root_folder + '\\Download_path'

    def import_dir(self):
        return self.root_folder + '\\Import_path'

    def import_deck_dir(self,deck):
        str = self.root_folder + '\\Import_path\\%s'
        return str % deck

    def import_fformat_file(self,deck, pos):
        str = self.import_deck_dir(deck) + '\\frontFormat_%d.txt'
        return str % pos

    def fformat_pattern(self):
        return 'frontFormat_(\\d*)\.txt'

    def import_bformat_file(self,deck, pos):
        str = self.import_deck_dir(deck) + '\\backFormat_%d.txt'
        return str % pos

    def import_wordslist_file(self,deck, pos):
        str = self.import_deck_dir(deck) + '\\wordslist_%d.txt'
        return str % pos

    def word_path(self,word):
        return self.download_dir() + '\\' + word

    def word_url(self, word):
        return 'http://cn.bing.com/dict/search?q=%s' % word

    def sentence_urls(self):
        return ['http://dict.youdao.com/example/mdia/audio/%s']#, 'http://dict.youdao.com/example/auth/%s'

    def log_folder(self):
        return self.root_folder + '\\logs'

    def log_file(self):
        str = self.log_folder() + '\\log_%s.txt'
        return str % time.strftime('%Y-%m-%d')

    def voice_lis_path(self,word,pos):
        str = self.word_path(word) + '\\Voice\\%d.txt'
        return str % pos

    def voice_pr_path(self,word,pos):
        str = self.word_path(word) + '\\Voice\\%d.mp3'
        return str % pos

    def picture_path(self,word, pos):
        str = self.word_path(word) + '\\Pic_%d.jpg'
        return str % pos

    def word_pr_path(self,word):
        return self.word_path(word) + '\\%s.mp3'

    def word_mean(self,word):
        return self.word_path(word) + '\\mean.txt'

    def word_addition(self,word):
        return self.word_path(word) + '\\addition.txt'

    def sentence_folder(self,word):
        return self.word_path(word) + '\\Voice'

    def clear_linefeeds(self,text):
        return text.strip().strip('\n').strip('\t')

    def getWordList(self, filePath):
        f = open(filePath, 'r')
        # 将单词字母小写
        words = []
        for word in f.readlines():
            word = word.strip('\n').strip(' ').lower()
            if word == '':
                continue
            l = re.findall(WORD_PATTERN, word)
            if len(l) != 0:
                words.append(word)
        f.close()
        words = list(set(words))
        return words