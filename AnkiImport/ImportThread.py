#!/usr/bin/env python
# encoding: utf-8

import threading
import logging

class importThread (threading.Thread):
    def __init__(self, threadName, process):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.process = process

        def run(self):
            Count = 0
            isFailure = False
            while (True):
                run = threadManager().CheckRunning()
                ImportWords = wordsManager().getFinishedWords()

                if (not run) and len(ImportWords) == 0:
                    logging.debug("No thread is running and no finished words.")
                    break

                (failure, newWords) = ImportCards(deckName, ImportWords, formatMap, realFormatList)

                if failure:
                    showFailureDialog()
                    isFailure = True
                    break
                Count += len(newWords)
                logging.debug(("This time import %d words." % len(newWords)))
                if len(newWords) == 0:
                    time.sleep(60)
                else:
                    file = open(Anki_common().import_wordslist_file(deckName, addid), 'a')
                    for newWord in newWords:
                        file.write(newWord + '\n')
                    file.close()

        def ImportCards(deckName, ImportWords, formatMap, realFormatList):
            if len(ImportWords) == 0:
                return (False, [])
            formatKeys = list(formatMap.keys())

            # Get the MediaImport deck id (auto-created if it doesn't exist)
            did = mw.col.decks.id(deckName)
            m = mw.col.models.byName("Basic")
            newWords = []
            failure = False
            for i, word in enumerate(ImportWords):
                note = notes.Note(mw.col, m)
                note.model()['did'] = did
                wordInfo = getWordInfo(word)
                for fKey in formatKeys:
                    if fKey == 'Voicelis':
                        voiceList = wordInfo['Voice']
                        formatVoice = formatMap[fKey]
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
                        formatVoice = formatMap[fKey]
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
                        formatPic = formatMap[fKey]
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

                note['Front'] = realFormatList[0] % wordInfo
                note['Back'] = realFormatList[1] % wordInfo

                if not mw.col.addNote(note):
                    # No cards were generated - probably bad template. No point
                    # trying to import anymore.
                    failure = True
                    break
                newWords.append(word)
                mw.progress.update(value=i)
                logging.debug(("Word:%s import as a card %d." % (word, i)))
            mw.progress.finish()
            mw.deckBrowser.refresh()
            return (failure, newWords)

