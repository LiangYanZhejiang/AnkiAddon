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
              u'addition.txt',
              u'权威英汉双解.txt',
              u'权威英汉双解_lis.txt',
              u'英汉.txt',
              u'英英.txt',
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

VOICE_MAX = 10

def doAnkiImport():
    reload(sys)
    sys.setdefaultencoding("utf-8")
    Anki_common(True)
    if not os.path.exists(Anki_common().log_folder()):
        os.mkdir(Anki_common().log_folder())

    log_format = '[%(asctime)s] [%(levelname)s] [%(filename)s] [%(module)s] [%(funcName)s] %(message)s'
    logging.basicConfig(format=log_format, filename=Anki_common().log_file(), filemode='a', level=logging.DEBUG)

    # Raise the main dialog for the add-on and retrieve its result when closed.
    (wordListFile, deckName, frontFormat, backFormat, ok) = ImportSettingsDialog().getDialogResult()
    if not ok:
        return
       
    #check format info
    if not (doCheckFormat(frontFormat) and doCheckFormat(backFormat)):
        return
    
    words = Anki_common().getWordList(wordListFile)

    #Import Words
    ImportWords = []
    Import_path = Anki_common().import_dir()
    if os.path.exists(Import_path):
        for filename in os.listdir(Import_path):
            if (os.path.isdir(Import_path + '\\' + filename) and filename in words):
                ImportWords.append(filename)
    else:
        os.mkdir(Import_path)

    words = list(set(words) - set(ImportWords))
    threadManager(words, ImportWords)

    (formatMap, realFormatList) = getFormatInfo([Anki_common().clear_linefeeds(frontFormat), Anki_common().clear_linefeeds(backFormat)])

    Count = 0
    isFailure = False
    while(True):
        run = threadManager().CheckRunning()
        ImportWords = wordsManager().getFinishedWords()

        if (not run) and len(ImportWords) == 0:
            break

        (failure, newCount) = ImportCards(deckName,ImportWords, formatMap, realFormatList)

        if failure:
            showFailureDialog()
            isFailure = True
            break
        Count += newCount
        if newCount == 0:
            time.sleep(60)

    if not isFailure:
        showCompletionDialog(Count)


def ImportCards(deckName,ImportWords,formatMap,realFormatList):
    if len(ImportWords) == 0:
        return (False, 0)
    formatKeys = list(formatMap.keys())
    
    # Get the MediaImport deck id (auto-created if it doesn't exist)
    did = mw.col.decks.id(deckName)
    m = mw.col.models.byName("Basic")
    mw.progress.start(max=len(ImportWords), parent=mw, immediate=True)
    newCount = 0
    failure = False
    for i, word in enumerate(ImportWords): 
        note = notes.Note(mw.col, m)
        note.model()['did'] = did
        wordInfo = getWordInfo(word)
        for fKey in formatKeys:
            if fKey == 'Voicelis':
                voiceList = wordInfo['Voice']
                formatVoice= formatMap[fKey]
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
                formatVoice= formatMap[fKey]
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
                formatPic= formatMap[fKey]
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
                    fname = mw.col.media.addFile()
                    str = u'[sound:%s]' % fname
                wordInfo[fKey] = str
            elif not (fKey in wordInfo.keys()):
                wordInfo[fKey] = ''
                
        note['Front'] = realFormatList[0] % wordInfo
        note['Back'] = realFormatList[1] % wordInfo

        if not mw.col.addNote(note):
            # No cards were generated - probably bad template. No point
            # trying to import anymore.
            failure = True
            break
        newCount += 1
        mw.progress.update(value=i)
    mw.progress.finish()
    mw.deckBrowser.refresh()
    return (failure, newCount)

#查询该文件夹是否为有效的单词信息存储文件夹
def doCheckWordInfo(word):
    wordPath = WORD_PATH % word
    existsFiles = set()
    if os.path.exists(wordPath):
        for filename in os.listdir(wordPath):
            existsFiles.add(filename)
    
    notExistsFiles = EXISTFILES - existsFiles
    if len(notExistsFiles) == 0:
        return True
    else:
        return False
    
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
        self.ImportDir = Anki_common().import_dir()
        self.form.ImportDir.setText(self.ImportDir)
        self.WordlistFile = ''
        self.DecksName = time.strftime(TIMEFORMAT, time.localtime(time.time()))
        self.form.DecksName.setText(self.DecksName)       
        self.exec_()
        

    def getDialogResult(self):
        if self.result() == QDialog.Rejected:
            return (None, None, None, None, False)
            
        return (self.WordlistFile, self.DecksName, self.FrontEdit, self.BackEdit, True)

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
    QMessageBox.about(mw, "Media Import Complete",
"""
<p>
Media import is complete and %s new notes were created. 
All generated cards are placed in the <b>MediaImport</b> deck.
<br><br>
Please refer to the introductory videos for instructions on 
<a href="https://youtube.com/watch?v=DnbKwHEQ1mA">flipping card content</a> or 
<a href="http://youtube.com/watch?v=F1j1Zx0mXME">modifying the appearance of cards.</a>
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

