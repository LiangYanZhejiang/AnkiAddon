#!/usr/bin/env python
# encoding: utf-8
import time

class Anki_common():
    root_folder = None
    def __init__(self):
        pass

    @staticmethod
    def InitRootFolder(isAddon):
        if isAddon:
            from aqt import mw
            Anki_common.root_folder = mw.pm.addonFolder() + '\\AnkiImport'
        else:
            import os
            Anki_common.root_folder = os.getcwd()

    @staticmethod
    def words_path():
        return Anki_common.root_folder + '\\Words'

    @staticmethod
    def import_dir():
        return Anki_common.root_folder + '\\Import_path'

    @staticmethod
    def word_path(word):
        return Anki_common.import_dir() + '\\' + word

    @staticmethod
    def word_url(word):
        return 'http://cn.bing.com/dict/search?q=%s' % word

    @staticmethod
    def sentence_urls():
        return ['http://dict.youdao.com/example/mdia/audio/%s', 'http://dict.youdao.com/example/auth/%s']

    @staticmethod
    def log_folder():
        return Anki_common.root_folder + '\\logs'

    @staticmethod
    def log_file():
        str = Anki_common.log_folder() + '\\log_%s.txt'
        return str % time.strftime('%Y-%m-%d')

    @staticmethod
    def voice_lis_path(word):
        return Anki_common.word_path(word) + '\\Voice\\%d.txt'

    @staticmethod
    def voice_pr_path(word):
        return Anki_common.word_path(word) + '\\Voice\\%d.mp3'

    @staticmethod
    def picture_path(word, pos):
        str = Anki_common.word_path(word) + '\\Pic_%d.jpg'
        return str % pos

    @staticmethod
    def word_pr_path(word):
        return Anki_common.word_path(word) + '\\%s.mp3'

    @staticmethod
    def word_mean(word):
        return Anki_common.word_path(word) + '\\mean.txt'

    @staticmethod
    def word_addition(word):
        return Anki_common.word_path(word) + '\\addition.txt'

    @staticmethod
    def sentence_folder(word):
        return Anki_common.word_path(word) + '\\Voice'

    @staticmethod
    def clear_linefeeds(text):
        return text.strip().strip('\n').strip('\t')