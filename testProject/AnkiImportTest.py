#!/usr/bin/env python
# encoding: utf-8
import time
import os
import re

TIMEFORMAT='%Y-%m-%d'
IMPORT_DIR = os.getcwd() + '\\Import_path'
WORD_PATH = IMPORT_DIR + '\\%s'
VOICE_LIS_PATH = WORD_PATH + '\\Voice\\%d.txt'
VOICE_PR_PATH = WORD_PATH + '\\Voice\\%d.mp3'
PICTURE_PATH = WORD_PATH + '\\Pic_%d.JPG'
WORD_PR_PATH = WORD_PATH + '\\%d.mp3'
           
EXISTFILES = {'pr_En.txt',
              'en.mp3',
              'pr_US.txt',
              'us.mp3',
              'mean.txt',
              'addition.txt',
              '权威英汉双解.txt',
              '权威英汉双解_lis.txt',
              '英汉.txt',
              '英英.txt',
              'Voice'}
              
ALLFILES = {'pr_En.txt',
              'en.mp3',
              'pr_US.txt',
              'us.mp3',
              'mean.txt',
              'addition.txt',
              '搭配.txt',
              '同义词.txt',
              '反义词.txt',
              '权威英汉双解.txt',
              '权威英汉双解_lis.txt',
              '英汉.txt',
              '英英.txt',
              'Voice'}
              
FORMAT_CONTENT = {'pr_En',
                  'en',
                  'pr_US',
                  'us',
                  'mean',
                  'addition',
                  '搭配',
                  '同义词',
                  '反义词',
                  '权威英汉双解',
                  '权威英汉双解_lis',
                  '英汉',
                  '英英',
                  'Voice',
                  'Word'}

PATTERN = r'%\((.*?)\)'
LIS_PATTERN = r'Voice_lis_(\d*)'
VOICE_PATTERN = r'Voice_pr_(\d*)'
PIC_PATTERN = r'Picture_(\d*)'
PATTERN_STR_S = '%%(%s)'
PATTERN_STR_D = '%%(%s)s'

PATTERN_LIST = [LIS_PATTERN, VOICE_PATTERN, PIC_PATTERN]

VOICE_MAX = 10

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
    picture = []
    wordPath = WORD_PATH % Word
    for filename in os.listdir(wordPath):
        if filename == 'Voice':
            voiceList = os.listdir(wordPath + '\\Voice')
            voice = []
            for i in range(1,VOICE_MAX + 1):
                lis = '%d.txt' % i
                lis_pr = '%d.mp3' % i
                if lis in voiceList and lis_pr in voiceList:
                    voice.append(i)
            wordInfo['Voice'] = voice
        elif filename in ALLFILES:
            file_s = filename.split('.')
            if file_s[1] == 'txt':
                file=open(wordPath + '\\' + filename, 'r', encoding = 'utf-8')
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
    if (len(exchangeList) == 0):
        return False
    print(len(exchangeList))
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
    
def main():
    wordListFile = os.getcwd() + '\\Words\\List001.txt'
    front = os.getcwd() + '\\Words\\frontFormat.txt'
    back = os.getcwd() + '\\Words\\backFormat.txt'
    frontResult = os.getcwd() + '\\Words\\frontResult_%s.txt'
    backResult = os.getcwd() + '\\Words\\backResult_%s.txt'
    f = open(front, 'r', encoding = 'utf-8')
    frontFormat = f.read()
    f.close
    
    f = open(back, 'r', encoding = 'utf-8')
    backFormat = f.read()
    f.close
       
    #check format info
    if not (doCheckFormat(frontFormat) and doCheckFormat(backFormat)):
        print('Format info is not suitable.')
        return
    
    f = open(wordListFile,'r', encoding='utf-8')
    #将单词字母小写
    words = []
    for word in f.readlines():
        words.append(word.strip('\n').lower())       
    f.close()
    #获取已有单词（未做），去除重复单词   
    words = list(set(words))
        
    #Import Words
    ImportWords = []
    for word in words:
        if doCheckWordInfo(word):
            ImportWords.append(word)
            
    if ImportWords == 0:
        return
           
    (formatMap, realFormatList) = getFormatInfo([frontFormat,backFormat])
    formatKeys=list(formatMap.keys())
    
    # Get the MediaImport deck id (auto-created if it doesn't exist)
    for i, word in enumerate(ImportWords):
        wordInfo = getWordInfo(word)
        for fKey in formatKeys:
            if fKey == 'Voicelis':
                voiceList = wordInfo['Voice']
                formatVoice= formatMap[fKey]
                for voicePos in range(formatVoice):
                    key = 'Voicelis_%d' % voicePos
                    if voicePos < len(voiceList):
                        f = open(VOICE_LIS_PATH % (word, voiceList[voicePos]), 'r', encoding = 'utf-8')
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
                        fname = key#mw.col.media.addFile(VOICE_PR_PATH % (word, voiceList[voicePos]))
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
                        fname = key#mw.col.media.addFile(PICTURE_PATH % (word, picList[picPos]))
                        str = u'<img src="%s">' % fname
                        wordInfo[key] = str
                    else:                        
                        wordInfo[key] = ''
            elif fKey == 'en' or fKey == 'us':
                fname = fKey#mw.col.media.addFile(WORD_PR_PATH % (word, voiceList[voicePos]))
                str = u'[sound:%s]' % fname                        
                wordInfo[fKey] = str
            elif not (fKey in wordInfo.keys()):
                wordInfo[fKey] = ''
                
        frontFile = frontResult % word
        backFile = backResult % word
        
        f = open(frontFile, 'w', encoding = 'utf-8')
        str = realFormatList[0] % wordInfo
        f.write(str)
        f.close()
        
        f = open(backFile, 'w', encoding = 'utf-8')
        f.write(realFormatList[1] % wordInfo)
        f.close()

if __name__ == "__main__":
    main()