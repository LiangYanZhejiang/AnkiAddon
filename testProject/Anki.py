﻿#!/usr/bin/env python
# encoding: utf-8
import requests
from bs4 import BeautifulSoup
import random
import sys
import os
import urllib
import socket
import logging

from anki_common import Anki_common

headers = [
    {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'},
    {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},
    {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'},
    {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0'},
    {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36'}
]

def do_savesentence(sentence_path, soup):
    #获取例句及读音
    os.mkdir(sentence_path)
    sentenceSeg = soup.find("div", id="sentenceSeg")
    sentenceNo = 1
    for sentence in sentenceSeg.find_all(class_ = 'se_li'):
        file_path = '%s\\%d.txt' %(sentence_path , sentenceNo)
        f = open(file_path, 'w', encoding = 'utf-8')
        f.write(sentence.text)
        voice = sentence.find(class_='bigaud')
        if voice != None:
            mousedown = voice.get('onmousedown')                
            i = mousedown.find("http")
            j = mousedown.find("mp3")
            if i != -1 and j != -1:                
                mp3link = mousedown[i:j+3]
                mp3_path = '%s\\%d.mp3' %(sentence_path , sentenceNo)
                urllib.urlretrieve(mp3link, mp3_path)
        sentenceNo = sentenceNo + 1

def beautiful_content(means, tag):
    result = ''
    for mean in means.contents:
        if hasattr(mean, 'text'):
            result = result + mean.text
            if (mean.name == tag):
                result = result + '\n'
            else:
                result = result + '   '
    return Anki_common.clear_linefeeds(result)

def get_map(means):
    if means == None:
       return
    tagmap = {}
    for mean in means.find_all(class_='tb_div'):
        for atag in mean.find_all('a'):
            if atag.text == None:
                continue            
            str = atag.get('onmousedown')
            if str == None:
                continue
            strlist = str.split(r"', '")
            str = strlist[0]
            x = str.find(r"('")
            y = str.find(r"')")
            if y == -1:
                str = str[x+2:]
            else:
                str = str[x+2:y]                
            tagmap[str+'id']=atag.text
    return tagmap
            
def do_request(word):
    source_code = requests.get(Anki_common.word_url(word), headers=random.choice(headers))

    # just get the code, no headers or anything
    plain_text = source_code.text

    # BeautifulSoup objects can be sorted through easy
    soup = BeautifulSoup(plain_text, "html.parser")
    wordinfo_path = Anki_common.word_path(word)

    log = 'Download word path %s' % wordinfo_path
    logging.debug(log)
    if os.path.exists(wordinfo_path):        
        return
        
    os.mkdir(wordinfo_path)
    
    #音标获取
    us_pr = soup.find('div', class_='hd_prUS')
    if us_pr != None:
        f = open(wordinfo_path + u'\\pr_US.txt', 'w')
        f.write(Anki_common.clear_linefeeds(us_pr.text))
        f.close()

    usa_pr = soup.find('div', class_='hd_pr')
    if us_pr != None:
        f = open(wordinfo_path + u'\\pr_En.txt', 'w')
        f.write(Anki_common.clear_linefeeds(usa_pr.text))
        f.close()

    #音标的读音获取
    mp3_us = True
    for pronounce in soup.find_all('a',class_='bigaud'):
        mouseover = pronounce.get('onmouseover')
        if mouseover == None:
            continue
        i = mouseover.find('http')
        j = mouseover.find('mp3')
        if i == -1 or j == -1:
            continue
        mp3link = mouseover[i:j+3]
        if (mp3_us and us_pr != None):
            mp3_path = wordinfo_path + '\\us.mp3'
        else:
            mp3_path = wordinfo_path + '\\en.mp3'
        
        urllib.urlretrieve(mp3link, mp3_path)
        mp3_us = False
        
    #单词意思获取
    f = open(Anki_common.word_mean(word), 'w')
    means = soup.find('div', class_='qdef')
    for mean in means.find_all('li'):
        f.write('%s\t%s\n' %(Anki_common.clear_linefeeds(mean.contents[0].text),
                               Anki_common.clear_linefeeds(mean.contents[1].text)))
    f.close()

    #单词的补充
    addition_mean = means.find(class_='hd_if')
    if addition_mean != None:
        f = open(Anki_common.word_addition(word), 'w')
        f.write(beautiful_content(addition_mean, 'a'))
        f.close()

    #单词的图片获取
    pictures = means.find(class_='img_area')
    if pictures != None:
        for pos, picture in enumerate(pictures.find_all('img')):
            piclink = picture.get('src')
            urllib.urlretrieve(piclink, Anki_common.picture_path(word, pos))
    
    #搭配，同义，反义的获取
    mean = means.find(class_='wd_div')
    tagmap = get_map(mean)

    if tagmap == None:
        tagmap_keys = []
    else:
        tagmap_keys=list(tagmap.keys())
        
    for key in tagmap_keys:
        f = open(wordinfo_path + '\\' + tagmap[key] + '.txt', 'w')
        mean = means.find(id=key)
        for detail in mean.find_all(class_='df_div2'):
                f.write('%s\t%s\n' %(Anki_common.clear_linefeeds(detail.contents[0].text),
                                     Anki_common.clear_linefeeds(detail.contents[1].text)))
        f.close()
        
    #权威英汉双解，英汉，英英的获取
    mean = means.find(class_='df_div')
    tagmap = get_map(mean)

    if tagmap == None:
        tagmap_keys = []
    else:
        tagmap_keys=list(tagmap.keys())
        
    for key in tagmap_keys:
        #网络的忽略之
        if key=='webid':
            continue

        #f获取的是释义
        #f2仅获取的是释义+例句
        f = open(wordinfo_path + '\\' + tagmap[key] + '.txt', 'w')
        mean = means.find(id=key)

        haslis = False
        if mean.find(class_ = 'se_lis') != None:
            haslis = True
            f2 = open(wordinfo_path + '\\' + tagmap[key] + '_lis.txt', 'w')

        segs = mean.find_all(class_='each_seg')
        if len(segs) == 0 : segs.append(mean)

        for seg in segs:
            pos = seg.find(class_='pos')
            if pos != None :
                f.write('%s\n' % Anki_common.clear_linefeeds(pos.text))
                if haslis: f2.write('%s\n' % Anki_common.clear_linefeeds(pos.text))
                        
            for table in seg.find_all('table'):
                lisFlag = False
                if haslis:
                    if 'li_exs' in table.parent.get('class'):
                        lisFlag = True
                        
                    sib = table.parent.previous_sibling
                    if sib != None and 'dis' in sib.get('class'):
                        f.write('%s\n' % Anki_common.clear_linefeeds(sib.text))
                        f2.write('%s\n' % Anki_common.clear_linefeeds(sib.text))

                fwrite = (not haslis) or (haslis and not lisFlag)
                    
                for tr in table.contents:                    
                    for td in tr.contents:
                        if hasattr(td.contents[0].contents[0], 'contents'):
                            for div in td.contents[0].contents:                    
                                if haslis: f2.write('%s' % Anki_common.clear_linefeeds(div.text))
                                if fwrite: f.write('%s' % Anki_common.clear_linefeeds(div.text))
                        else:
                            if haslis: f2.write('%s\t' % Anki_common.clear_linefeeds(td.text))
                            if fwrite: f.write('%s\t' % Anki_common.clear_linefeeds(td.text))
                    if haslis: f2.write('\n')
                    if fwrite: f.write('\n')
                if haslis: f2.write('\n')
                if fwrite: f.write('\n')
                
        if haslis: f2.close()
        f.close()

    #原音获取
    sentence_path = Anki_common.sentence_folder(word)
    os.mkdir(sentence_path)

    totalNo = 1
    for lis_url in Anki_common.sentence_urls():
        sentence_url = lis_url % word
        sentence_code = requests.get(sentence_url, headers=random.choice(headers), timeout = 15)
        # just get the code, no headers or anything
        sentence_text = sentence_code.text

        # BeautifulSoup objects can be sorted through easy
        sentence_soup = BeautifulSoup(sentence_text, "html.parser")
        sentences = sentence_soup.find("ul", class_="ol")
                
        if sentences == None:
            return

        for sentenceNo, sentence in enumerate(sentences.find_all('li')):
            if sentenceNo >= 5:
                break
        
            content = sentence.find('p')
            file_path = '%s\\%d.txt' %(sentence_path, totalNo)
            f = open(file_path, 'w')
            f.write(Anki_common.clear_linefeeds(content.text))
            f.close()
            
            aTag = sentence.find_all('a')
            if aTag == None:
                continue        

            if len(aTag) == 2 :
                mp3link = aTag[1].get('href')
            else:
                mp3link = aTag[0].get('data-rel')
            if mp3link != None:            
                mp3_path = '%s\\%d.mp3' %(sentence_path , totalNo)
                try:
                    opener = urllib.FancyURLopener({})
                    opener.version = random.choice(headers)['User-Agent']
                    urllib._urlopener = opener
                    urllib.urlretrieve(mp3link, mp3_path)
                    log = 'Download %s' % mp3link
                    logging.debug(log)
                except Exception as ex:
                    log = 'Exception happened, can\'t download mp3:(%s)(%s).\nException:%s' % (content.text,mp3link,ex)
                    logging.error(log)

            totalNo = totalNo + 1

def import_words(words):
    socket.setdefaulttimeout(5)

    existsWords = set()
    Import_path = Anki_common.import_dir()
    if os.path.exists(Import_path):
        for filename in os.listdir(Import_path):
            if (os.path.isdir(Import_path + '\\' + filename)):
                existsWords.add(filename)
    else:
        os.mkdir(Import_path)

    # 去除重复单词
    words = list(set(words) - existsWords)

    times = 0
    for word in words:
        try:
            do_request(word)
            times = 0
        except requests.exceptions.ConnectionError as e:
            times += 1
            tips = "Can't get Word--%s, exception happened." % word
            logging.exception(tips)

            if times >= 3:
                print("Please check your internet connection.")
                break

def main():
    if not os.path.exists(Anki_common.words_path()):
        tips = "Please give your wordlist in folder: %s." % Anki_common.words_path()
        logging.error(tips)

    words = []
    words_path = Anki_common.words_path()
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

    Anki_common.InitRootFolder(False)

    if not os.path.exists(Anki_common.log_folder()):
        os.mkdir(Anki_common.log_folder())

    log_format = '[%(asctime)s] [%(levelname)s] [%(filename)s] [%(module)s] [%(funcName)s] %(message)s'
    logging.basicConfig(format=log_format,filename=Anki_common.log_file(), filemode='a',level=logging.DEBUG)

    #console = logging.StreamHandler()
    #console.setLevel(logging.DEBUG)
    #console.setFormatter(log_format)
    #logging.getLogger('').addHandler(console)

    main()