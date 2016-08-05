#!/usr/bin/env python
# encoding: utf-8
import time
import requests
from bs4 import BeautifulSoup
import random
import sys
import os
import urllib

words_path = os.getcwd() + "\\Words"
Import_path = os.getcwd() + "\\Import_path"
word_url = "http://cn.bing.com/dict/search?q=%s"

headers = [
    {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'},
    {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},
    {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'},
    {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0'},
    {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36'}
]

def beautiful_content(means, tag):
    result = ''
    for mean in means.descendants:
        if hasattr(mean, 'text'):
            result = result + mean.text
            if (mean.name == tag):
                result = result + '\n'
            else:
                result = result + '   '
    return result
            
def do_request(word):
    global Import_path, headers

    url = word_url % word
    source_code = requests.get(url, headers=random.choice(headers), timeout = 15)

    # just get the code, no headers or anything
    plain_text = source_code.text
    # BeautifulSoup objects can be sorted through easy
    soup = BeautifulSoup(plain_text, "html.parser")
    wordinfo_path = Import_path + '\\' + word

    print(wordinfo_path)
    if os.path.exists(wordinfo_path):        
        return
        
    os.mkdir(wordinfo_path)
    
    #音标获取
    f = open(wordinfo_path + '\\' + 'pr_US.txt', 'w', encoding='utf-8')
    us_pr = soup.find("div", class_="hd_prUS")
    f.write(us_pr.text)
    f.close()
    f = open(wordinfo_path + '\\' + 'pr_En.txt', 'w', encoding='utf-8')
    usa_pr = soup.find("div", class_="hd_pr")
    f.write(usa_pr.text)
    f.close()

    #音标的读音获取
    mp3_us = True
    for pronounce in soup.find_all("a",class_="bigaud"):
        mouseover = pronounce.get("onmouseover")
        if mouseover == None:
            continue
        i = mouseover.find("http")
        j = mouseover.find("mp3")
        if i == -1 or j == -1:
            continue
        mp3link = mouseover[i:j+3]
        if (mp3_us):
            mp3_path = wordinfo_path + "\\us.mp3"
        else:
            mp3_path = wordinfo_path + "\\en.mp3"
        
        urllib.request.urlretrieve(mp3link, mp3_path)
        mp3_us = False
        
    #单词意思获取
    word_mean = wordinfo_path + "\\mean.txt"
    f = open(word_mean, 'w', encoding='utf-8')
    means = soup.find("div", class_="qdef")
    for mean in means.find_all('li'):
        f.write(mean.text + "\n")
    f.close()

    #单词的补充
    addition_path = wordinfo_path + "\\addition.txt"
    addition_mean = means.find(class_='hd_if')
    if addition_mean != None:
        f = open(addition_path, 'w', encoding='utf-8')
        f.write(beautiful_content(addition_mean, 'a'))
        f.close()
    
    
    #搭配，同义，反义,权威英汉双解，英汉，英英的获取
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
    
    #f获取的是释义+例句
    #f2仅获取的是释义
    tagmap_keys=list(tagmap.keys())
    for key in tagmap_keys:
        #网络的忽略之
        if key=='webid':
            continue
            
        f = open(wordinfo_path + '\\' + tagmap[key] + '.txt', 'w', encoding = 'utf-8')
        mean = means.find(id=key)
        sentence= mean.find(class_='li_sen')
        #权威英汉双解，英汉，英英
        if (sentence != None):
            f2 = open(wordinfo_path + '\\' + tagmap[key] + '_lis.txt', 'w', encoding = 'utf-8')
            f2.write(sentence.text)
            for no_lis in mean.find_all(class_='se_lis'):
                f.write(no_lis.text)
            f2.close()
        #搭配，同义，反义
        else:
            f.write(mean.text)
        f.close()
        
    #获取例句及读音
    sentence_path = wordinfo_path + '\\例句'
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
                urllib.request.urlretrieve(mp3link, mp3_path)            
        sentenceNo = sentenceNo + 1
        


if __name__ == "__main__":
    if not os.path.exists(words_path):
        tips = "Please give your wordlist in folder: %s." % words_path
        print(tips)

    existsWords = set()
    if os.path.exists(Import_path):
        for filename in os.listdir(Import_path):
            if(os.path.isdir(Import_path + '\\' + filename)):
                existsWords.add(filename)
    else:
        os.mkdir(Import_path)    

    for filename in os.listdir(words_path):
        if(os.path.isdir(words_path + '\\' + filename)):
            continue;
        f = open(words_path + '\\' + filename,'r', encoding='utf-8')
        
        #将单词字母小写
        words = []
        for word in f.readlines():
            words.append(word.strip('\n').lower())       
        f.close()
        
        #去除重复单词
        words = list(set(words) - existsWords)
        
        for word in words:
            try:
                do_request(word)
            except requests.exceptions.ConnectionError as e:                
                tips = "Can't get Word--%s, exception happened." % word        
                print(tips)
                print(e)

                wordinfo_path = Import_path + '\\' + word
                if os.path.exists(wordinfo_path):
                    import shutil
                    shutil.rmtree(wordinfo_path)
    