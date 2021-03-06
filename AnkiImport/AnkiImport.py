#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf-8 -*-
from aqt import mw
from aqt.qt import *
from aqt import editor
from anki import notes
import ImportUI
import logging
from anki_common import Anki_common
from DownLoadThread import threadManager
from DownLoadThread import wordsManager
from anki_common import singleton

import time
import os
import re
from PyQt4 import QtGui
import sys
from datetime import datetime
import codecs

TIMEFORMAT='%Y-%m-%d'

EXISTFILES = {u'pr_En.txt',
              u'en.mp3',
              u'mean.txt',
              u'Voice'}
              
ALLFILES = {u'pr_En.txt',
              u'en.mp3',
              u'pr_US.txt',
              u'us.mp3',
              u'mean.txt',
              u'addition.txt',
              u'搭配.txt',
              u'同义词.txt',
              u'反义词.txt',
              u'权威英汉双解.txt',
              u'权威英汉双解_lis.txt',
              u'英汉.txt',
              u'英英.txt',
              u'Voice'}
              
FORMAT_CONTENT = {u'pr_En',
                  u'en',
                  u'pr_US',
                  u'us',
                  u'mean',
                  u'addition',
                  u'搭配',
                  u'同义词',
                  u'反义词',
                  u'权威英汉双解',
                  u'权威英汉双解_lis',
                  u'英汉',
                  u'英英',
                  u'Voice',
                  u'Word'}

PATTERN = u'%\\((.*?)\\)'
LIS_PATTERN = u'Voice_lis_(\\d*)'
VOICE_PATTERN = u'Voice_pr_(\\d*)'
PIC_PATTERN = u'Picture_(\\d*)'
PATTERN_STR_S = '%%(%s)'
PATTERN_STR_D = '%%(%s)s'

PATTERN_LIST = [LIS_PATTERN, VOICE_PATTERN, PIC_PATTERN]

FOLDER_CANNOT_INCLUDE = ['/',':','*','?','"','<','>','|','\n']
FOLDER_CANNOT_BE = {'CON','PRN','AUX','CLOCK$','NUL','COM1','COM2','COM3','COM4','COM5','COM6','COM7','COM8','COM9,','LPT1'}

VOICE_MAX = 10

@singleton
class ImportManager():
    def init(self,wordsListFile, deckName, frontFormat,backFormat):
        self.__frontFormat = frontFormat
        self.__backFormat = backFormat
        self.__words = Anki_common().getWordList(wordsListFile)
        self.__deckName = deckName
        self.__initWordsImported()
        self.__initDownloadWords()
        (self.__formatMap, self.__realFormatList) = getFormatInfo([frontFormat, backFormat])

    # 获取在该deck上已经以相同的格式导入的的单词
    def __initWordsImported(self):
        deck = self.__deckName
        frontFormat = self.__frontFormat
        backFormat = self.__backFormat
        ####
        import_folder = Anki_common().import_dir()
        if not os.path.exists(import_folder):
            os.mkdir(import_folder)

        deck_folder = Anki_common().import_deck_dir(deck)
        words = []
        addid = -1
        maxid = 0

        if not os.path.exists(deck_folder):
            os.mkdir(deck_folder)
        else:
            for filename in os.listdir(deck_folder):
                relist = re.findall(Anki_common().fformat_pattern(), filename)
                if len(relist) == 0:
                    continue
                id = int(relist[0])
                if id > maxid:
                    maxid = id

                frontFile = Anki_common().import_fformat_file(deck, id)
                backFile = Anki_common().import_bformat_file(deck, id)
                wordslistFile = Anki_common().import_wordslist_file(deck, id)
                if (not os.path.exists(backFile)) or (not os.path.exists(wordslistFile)):
                    continue

                file = open(frontFile, 'r')
                str = file.read()
                file.close()

                if str != frontFormat:
                    continue

                file = open(backFile, 'r')
                str = file.read()
                file.close()

                if str != backFormat:
                    continue

                words = Anki_common().getWordList(wordslistFile)
                addid = id
                break

        if addid == -1:
            addid = maxid + 1
            file = open(Anki_common().import_fformat_file(deck, addid), 'w')
            file.write(frontFormat)
            file.close()

            file = open(Anki_common().import_bformat_file(deck, addid), 'w')
            file.write(backFormat)
            file.close()
        ###
        logging.debug(('Addid:%d, importedWords:%d' % (addid, len(words))))
        self.__addid = addid
        self.__ImportedWords = words

    #获取已经下载的单词
    def __initDownloadWords(self):
        downloadWords = []
        Download_path = Anki_common().download_dir()
        if os.path.exists(Download_path):
            for filename in os.listdir(Download_path):
                if (os.path.isdir(Download_path + '\\' + filename) and filename in self.__words):
                    if self.__doCheckWordInfo(filename):
                        downloadWords.append(filename)
        else:
            os.mkdir(Download_path)
        logging.debug(("%d words is already added." % len(downloadWords)))
        self.__downloadWords = downloadWords

    def getDownloadWords(self):
        return list(set(self.__downloadWords) - set(self.__ImportedWords) - FOLDER_CANNOT_BE)

    def getImportWords(self):
        return list(set(self.__words) - set(self.__ImportedWords) - set(self.__downloadWords) - FOLDER_CANNOT_BE)


    # 查询该文件夹是否为有效的单词信息存储文件夹
    def __doCheckWordInfo(self, word):
        wordPath = Anki_common().word_path(word)
        existsFiles = set()
        if os.path.exists(wordPath):
            for filename in os.listdir(wordPath):
                existsFiles.add(filename)

        notExistsFiles = EXISTFILES - existsFiles
        if len(notExistsFiles) == 0:
            return True
        else:
            return False

    def startImport(self):
        downloadWords = self.getDownloadWords()
        words = self.getImportWords()

        logging.debug(("%d words need download, %d words is already download." % (len(words), len(downloadWords))))
        if len(words) == 0 and len(downloadWords) == 0:
            showCompletionDialog(0)
            return

        threadManager().init(words, downloadWords)

        totalWordsNum = len(words) + len(downloadWords)
        mw.progress.start(totalWordsNum, parent=mw, immediate=True)

        Count = 0
        isFailure = False
        while (True):
            run = threadManager().CheckRunning()
            ImportWords = wordsManager().getFinishedWords()

            if (not run) and len(ImportWords) == 0:
                logging.debug("No thread is running and no finished words.")
                break

            (failure, newWords) = self.ImportCards(ImportWords,Count)

            if failure:
                showFailureDialog()
                isFailure = True
                break
            Count += len(newWords)
            logging.debug(("This time import %d words." % len(newWords)))
            if len(newWords) != 0:
                file = open(Anki_common().import_wordslist_file(self.__deckName, self.__addid), 'a')
                for newWord in newWords:
                    file.write(newWord + '\n')
                file.close()

        mw.progress.finish()
        mw.deckBrowser.refresh()
        if not isFailure:
            showCompletionDialog(Count)

    def ImportCards(self, ImportWords,position):
        if len(ImportWords) == 0:
            return (False, [])
        formatKeys = list(self.__formatMap.keys())

        # Get the MediaImport deck id (auto-created if it doesn't exist)
        did = mw.col.decks.id(self.__deckName)
        m = mw.col.models.byName("Basic")

        newWords = []
        failure = False
        i = position
        for word in ImportWords:
            note = notes.Note(mw.col, m)
            note.model()['did'] = did
            wordInfo = getWordInfo(word)
            for fKey in formatKeys:
                if fKey == 'Voicelis':
                    voiceList = wordInfo['Voice']
                    formatVoice = self.__formatMap[fKey]
                    for voicePos in range(formatVoice):
                        key = 'Voicelis_%d' % voicePos
                        if voicePos < len(voiceList):
                            f = open(Anki_common().voice_lis_path(word, voiceList[voicePos]), 'r')
                            str = f.read()
                            f.close()
                            wordInfo[key] = str
                        else:
                            wordInfo[key] = ''
                elif fKey == 'Voicepr':
                    voiceList = wordInfo['Voice']
                    formatVoice = self.__formatMap[fKey]
                    for voicePos in range(formatVoice):
                        key = 'Voicepr_%d' % voicePos
                        if voicePos < len(voiceList):
                            fname = mw.col.media.addFile(Anki_common().voice_pr_path(word, voiceList[voicePos]))
                            str = u'[sound:%s]' % fname
                            wordInfo[key] = str
                        else:
                            wordInfo[key] = ''
                elif fKey == 'Pic':
                    picList = wordInfo['Picture']
                    formatPic = self.__formatMap[fKey]
                    for picPos in range(formatPic):
                        key = 'Pic_%d' % picPos
                        if picPos < len(picList):
                            fname = mw.col.media.addFile(Anki_common().picture_path(word, picList[picPos]))
                            str = u'<img src="%s">' % fname
                            wordInfo[key] = str
                        else:
                            wordInfo[key] = ''
                elif fKey == 'en' or fKey == 'us':
                    pr_path = Anki_common().word_pr_path(word, fKey)
                    str = ''
                    if os.path.exists(pr_path):
                        fname = mw.col.media.addFile(pr_path)
                        str = u'[sound:%s]' % fname
                    wordInfo[fKey] = str
                elif not (fKey in wordInfo.keys()):
                    wordInfo[fKey] = ''

            note['Front'] = self.getCardContent(self.__realFormatList[0],wordInfo)
            note['Back'] = self.getCardContent(self.__realFormatList[1],wordInfo)

            if not mw.col.addNote(note):
                # No cards were generated - probably bad template. No point
                # trying to import anymore.
                failure = True
                break
            newWords.append(word)
            i += 1
            mw.progress.update(value=i)
            logging.debug(("Word:%s imported." % word))
        return (failure, newWords)

    def getCardContent(self, formatlist, wordInfo):
        content = formatlist % wordInfo
        contentList = content.split('\n')
        result = ''
        for info in contentList:
            if result == '':
                result = info
            else:
                result = '%s<div>%s</div>' % (result, info)
        return result


def doAnkiImport():
    reload(sys)
    sys.setdefaultencoding("utf-8")
    Anki_common(True)
    if not os.path.exists(Anki_common().log_folder()):
        os.mkdir(Anki_common().log_folder())

    log_format = '[%(asctime)s] [%(levelname)s] [%(filename)s] [%(module)s] [%(funcName)s] %(message)s'
    logging.basicConfig(format=log_format, filename=Anki_common().log_file(), filemode='a', level=logging.DEBUG)

    # Raise the main dialog for the add-on and retrieve its result when closed.
    (wordsListFile, deckName, frontFormat, backFormat, ok) = ImportSettingsDialog().getDialogResult()
    if not ok:
        return

    ImportManager().init(wordsListFile, deckName, frontFormat, backFormat)
    ImportManager().startImport()

#获取单词的文件信息    
#存储格式为：
#txt: name-->content
#jpg: 'Picture'-->jpg list
#mp3: name-->1   mp3为单词发音
#例句：'Voice'-->txt&mp3 name list
def getWordInfo(Word):
    wordInfo = {'Word':Word}
    wordInfo['Voice'] = []
    picture = []
    wordPath = Anki_common().word_path(Word)
    for filename in os.listdir(wordPath):
        if filename == 'Voice':
            voiceList = os.listdir(wordPath + '\\Voice')
            voice = []
            for i in range(1,VOICE_MAX+1):
                lis = '%d.txt' % i
                lis_pr = '%d.mp3' % i
                if lis in voiceList and lis_pr in voiceList:
                    voice.append(i)
            wordInfo['Voice'] = voice
        elif filename in ALLFILES:
            file_s = filename.split('.')
            if file_s[1] == 'txt':
                file=open(wordPath + '\\' + filename, 'r')
                str = file.read()
                file.close()
                wordInfo[file_s[0]] = str
            elif file_s[1] == 'mp3':
                wordInfo[file_s[0]] = 1
            elif file_s[1] == 'jpg':
                picture.append(filename)
    
    wordInfo['Picture'] = picture
        
    return wordInfo

#检查格式是否符合要求
def doCheckFormat(wordFormat):
    exchangeList = re.findall(PATTERN, wordFormat)
    if len(exchangeList) == 0:
        return False
    lastlist = list(set(exchangeList) - FORMAT_CONTENT)
    for content in lastlist:
        num = 0
        for pattern in PATTERN_LIST:
            num = num + len(re.findall(pattern, content))
        
        if num == 0:
            return False    
    return True        

#获取Format需要的信息
def getFormatInfo(wordList):
    resultMap = {'Voicelis':0, 'Pic':0, 'Voicepr':0}
    resultFormatList = []
    
    for wordFormat in wordList:
        resultFormat = wordFormat
        exchangeList = re.findall(PATTERN, wordFormat)
        exchangeList = list(set(exchangeList))
        for content in exchangeList:
            sstr = PATTERN_STR_S % content
            dstr = ''
            if content in FORMAT_CONTENT:
                resultMap[content] = 1
                dstr = PATTERN_STR_D % content
            else:
                for pattern in PATTERN_LIST:
                    listNum = re.findall(pattern,content)
                    if len(listNum) == 0:
                        continue
                    
                    assert len(listNum) == 1
                    num = int(listNum[0])
                    if num > 10: num = 10
                    if num > 0:
                        if pattern == LIS_PATTERN:
                            for i in range(0, num):
                                str = '%%(Voicelis_%d)s' % i
                                dstr = dstr + str
                                lisnum = resultMap['Voicelis']
                                if (num > lisnum):
                                    resultMap['Voicelis'] = num
                        elif pattern == VOICE_PATTERN:
                           for i in range(0, num):
                                str = '%%(Voicelis_%d)s%%(Voicepr_%d)s\n' % (i,i)
                                dstr = dstr + str
                                lisnum = resultMap['Voicelis']
                                if (num > lisnum):
                                    resultMap['Voicelis'] = num
                                prnum = resultMap['Voicepr']
                                if (num > prnum):
                                    resultMap['Voicepr'] = num
                        else:#PIC_PATTERN
                            for i in range(0, num):
                                str = '%%(Pic_%d)s' % i
                                dstr = dstr + str
                                picnum = resultMap['Pic']
                                if (num > picnum):
                                    resultMap['Pic'] = num

            resultFormat = resultFormat.replace(sstr, dstr)
                    
        resultFormatList.append(resultFormat)

    return (resultMap, resultFormatList)

class ImportSettingsDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self, mw)
        self.form = ImportUI.Ui_Form()
        self.form.setupUi(self)
        self.form.buttonBox.accepted.connect(self.accept)
        self.form.buttonBox.rejected.connect(self.reject)
        self.form.browse.clicked.connect(self.onBrowse)
        self.ImportDir = Anki_common().download_dir()
        self.form.ImportDir.setText(self.ImportDir)
        self.WordlistFile = ''
        self.DecksName = time.strftime(TIMEFORMAT, time.localtime(time.time()))
        self.form.DecksName.setText(self.DecksName)       
        self.exec_()
        

    def getDialogResult(self):
        if self.result() == QDialog.Rejected:
            return (None, None, None, None, False)

        front = Anki_common().clear_linefeeds(self.FrontEdit)
        back = Anki_common().clear_linefeeds(self.BackEdit)
            
        return (self.WordlistFile, self.DecksName, front, back, True)

    def onBrowse(self):
        """Show the directory selection dialog."""
        path = unicode(
            QFileDialog.getOpenFileName(mw, "Words list file",".","Text File(*.txt)"))

        self.WordlistFile = path
        self.form.WordlistFile.setText(self.WordlistFile)
        self.form.WordlistFile.setStyleSheet("")

    def accept(self):
        # Show a red warning box if the user tries to import without selecting
        # a directory.
        if not self.WordlistFile:
            self.form.WordlistFile.setStyleSheet("border: 1px solid red")
            return
        self.DecksName = self.form.DecksName.text()
        self.FrontEdit = self.form.FrontEdit.toPlainText()
        self.BackEdit = self.form.BackEdit.toPlainText()

        self.form.DecksName.setStyleSheet("")
        self.form.FrontEdit.setStyleSheet("")
        self.form.BackEdit.setStyleSheet("")

        words = Anki_common().getWordList(self.WordlistFile)
        if len(words) == 0:
            self.form.WordlistFile.setStyleSheet("border: 1px solid red")
            showErrorDialog("Can't get words from file:%s." % self.WordlistFile)
            return
        if self.DecksName == '':
            self.form.DecksName.setStyleSheet("border: 1px solid red")
            return
        deckName = self.DecksName.upper()
        for char in FOLDER_CANNOT_INCLUDE:
            if char in deckName:
                showErrorDialog(("DeckName canot include %s ." % char))
                self.form.DecksName.setStyleSheet("border: 1px solid red")
                return
        for name in FOLDER_CANNOT_BE:
            if name == deckName:
                showErrorDialog(("DeckName canot be %s ." % self.DecksName))
                self.form.DecksName.setStyleSheet("border: 1px solid red")
                return
        if self.FrontEdit == '':
            self.form.FrontEdit.setStyleSheet("border: 1px solid red")
            return
        if not doCheckFormat(self.FrontEdit):
            self.form.FrontEdit.setStyleSheet("border: 1px solid red")
            showErrorDialog("Front format is wrong.")
            return
        if self.BackEdit == '':
            self.form.BackEdit.setStyleSheet("border: 1px solid red")
            return
        if not doCheckFormat(self.BackEdit):
            self.form.BackEdit.setStyleSheet("border: 1px solid red")
            showErrorDialog("Back format is wrong.")
            return
        QDialog.accept(self)

def showCompletionDialog(newCount):
    if newCount == 0:
        QMessageBox.about(mw, "Media Import Complete","No words need to importing...")
    else:
        QMessageBox.about(mw, "Media Import Complete",
"""
<p>
Media import is complete and %s new notes were created.
</p>""" % newCount)

def showFailureDialog():
    QMessageBox.about(mw, "Media Import Failure",
"""
<p>
Failed to generate cards and no media files were imported. Please ensure the
note type you selected is able to generate cards by using a valid
<a href="http://ankisrs.net/docs/manual.html#cards-and-templates">card template</a>.
</p>
""")

def showErrorDialog(reason):
    QMessageBox.about(mw, "Error",reason)

action = QAction("Words Import...", mw)
mw.connect(action, SIGNAL("triggered()"), doAnkiImport)
mw.form.menuTools.addAction(action)

