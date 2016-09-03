#!/usr/bin/env python
# encoding: utf-8

import threading
import logging
import urllib2
from WordDownLoad import do_request
from anki_common import singleton

THREAD_NUM_MAX = 10

class downloadThread (threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.wordslist = wordsManager().getWordsForDownload(threadID)

    def run(self):
        while True:
            if len(self.wordslist) == 0:
                break

            times = 0
            for word in self.wordslist:
                try:
                    do_request(word)
                    times = 0
                    wordsManager().setWordFinished(self.threadID, word)
                except urllib2.URLError as e:
                    times += 1
                    tips = "Can't get Word:%s, exception happened." % word
                    logging.exception(tips)

                    if times >= 3:
                        logging.errot("Exceptions happened more than 3 times, please check your connection.")
                        break

            self.wordslist = wordsManager().getWordsForDownload(self.threadID)
        else:
            tip = "Thread %d is Closed."
            logging.info(tips)

@singleton
class wordsManager():
    def __init__(self, wordslist, finishedlist):
        self.mutex = threading.Lock()
        self.wordslist = wordslist
        self.downloadMap = {}
        self.finishedlist = finishedlist

    def getWordsForDownload(self, threadID):
        if len(self.wordslist) == 0:
            return None

        wordsNum = self.downLoadNum()

        wordsNum = wordsNum/THREAD_NUM_MAX/2
        if wordsNum == 0:
            wordsNum = 1

        words = []
        self.mutex.acquire()
        downloadlist = self.getDownloadList_(threadID)

        if len(self.wordslist) != 0:
            if wordsNum > len(self.wordslist):
                wordsNum = len(self.wordslist)
            words = self.wordslist[len(self.wordslist) - wordsNum:len(self.wordslist) - 1]
            self.wordslist = list(set(self.wordslist) - set(words))
            self.downloadMap[threadID] = list(set(downloadlist) | set(words))
        self.mutex.release()

        return words

    def setWordFinished(self, threadID, word):
        if word != None:
            self.mutex.acquire()
            self.downloadMap[threadID].remove(word)
            self.finishedlist.append(word)
            self.mutex.release()

    def downLoadNum(self):
        self.mutex.acquire()
        wordsNum = len(self.wordslist)
        for dlist in self.downloadMap.values():
            if dlist != None:
                wordsNum += len(dlist)
        self.mutex.release()
        return wordsNum

    def RedoWordlist(self, threadID):
        self.mutex.acquire()
        downloadlist = self.downloadMap.pop(threadID)
        if downloadlist != None and len(downloadlist) != 0:
            self.wordslist = list(set(self.wordslist) | set(downloadlist))
        self.mutex.release()

    def getFinishedWords(self):
        if len(self.finishedlist) == 0:
            return []

        self.mutex.acquire()
        words = self.finishedlist
        self.finishedlist = []
        self.mutex.release()
        return words

    def getDownloadList_(self, threadID):
        downloadlist = []
        if threadID in self.downloadMap.keys():
            downloadlist = self.downloadMap[threadID]

        if downloadlist == None:
            downloadlist = []
        return downloadlist

@singleton
class threadManager():
    def __init__(self, wordslist, finishedlist):
        wordsManager(wordslist, finishedlist)
        self.threads = {}
        for threadID in range(1, THREAD_NUM_MAX):
            thread = downloadThread(threadID)
            self.threads[threadID] = thread
            thread.start()

    def CheckRunning(self):
        for threadID, thread in self.threads.items():
            if thread != None:
                if not thread.is_alive():
                    wordsManager().RedoWordlist(threadID)
                    del (self.threads[threadID])
            else:
                del(self.threads[threadID])

        if len(self.threads) == 0:
            return False

        return True