import re
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from .process_vocabs import softEndingMasculine, softEndingFeminine, softEndingWords, yatRoots, yatExcl, usRoots, usExcl, abbreviations, yatNotTe, verbsHomonymsTe
import nltk
nltk.download('punkt')

from .pos_tagger import tag_pos

class Converter():

    cons = {"б", "в", "г", "д", "ж", "з", "к", "л", "м", "н", "п", "р", "с", "т", "ф", "х", "ц", "ч", "ш", "щ"}
    vowels = {"а", "ъ", "о", "у", "е", "и", "ѣ", "ѫ"}
    no_succeeding_yat = vowels.union({"ч", "ш", "ж"}) # letters after which we can't have a yat vowel
    expandedVS = {'във', 'със'}
    usHomographs = {'кът', 'път', 'прът'}
    usSecondVowel = {'гълъб', 'жълъд'}
    yatFullExclusions = {'сте', 'вещ', 'лев', 'лева'}
    yatFullWords = {'ляв', 'лява', 'лявата', 'бях', 'бяха', 'бяхме','вежда', 'вежди', 'веждата', 'веждите', 'де', 'бе'}
    yatDoubleRoots = {'бележ', 'белез', 'белег', 'белех', 'белел', 'беляз', 'белял', 'белях', 'предмет'}
    yatPrefixes = {'пре', 'две', 'ня'}
    yatSuffixes = {'еше', 'еха'}
    feminineTheEndings = {'тта', 'щта'}
    exclusionWords = {('въстава', 'възстава'), ('въстан', 'възстан'), ('нишк', 'нищк'), ('нужни', 'нуждни'), ('овошк', 'овощк'), ('празник', 'праздник'), ('празнич', 'празднич'), ('сърц', 'сърдц'), ('сърчи', 'сърдчи')}
    softEndingMasculine, softEndingFeminine, softEndingWords, yatRoots, yatExcl, usRoots, usExcl, abbreviations, yatNotTe, verbsHomonymsTe = softEndingMasculine, softEndingFeminine, softEndingWords, yatRoots, yatExcl, usRoots, usExcl, abbreviations, yatNotTe, verbsHomonymsTe

    def __init__(self):
        pass

    def __replaceKeepCase(self, word, replacement, text):
        '''
        Replace substring, but keep case of original string

        "Borrowed" with some modifications from https://stackoverflow.com/questions/24893977/whats-the-best-way-to-regex-replace-a-string-in-python-but-keep-its-case
        '''

        def func(match):
            g = match.group()
            if g.islower(): return replacement.lower()
            if g.istitle(): return replacement.title()
            if g.isupper(): return replacement.upper()
            return replacement
        return re.sub(re.escape(word), func, text, count=1, flags=re.I)


    def __getYatVowel(self, word):
        '''
        Get the vowel to be changed into yat
        '''
        index_e = -1 if 'е' not in word else word.index('е')
        index_ya = -1 if 'я' not in word else word.index('я')
        if index_ya == -1:
            vowel = 'е'
        elif index_e == -1:
            vowel = 'я'
        elif index_ya > index_e:
            vowel = 'е'
        else:
            vowel = 'я'

        return vowel


    def checkEnding(self, i, words, currentWord):
        '''
        Place yer vowels at the end of words ending in consonants
        '''
        if currentWord[-1] in self.cons:
            if currentWord in self.abbreviations:
                return

            if currentWord in self.expandedVS:
                words[i] = words[i][:1] + 'ъ'
                return

            if currentWord in self.softEndingWords:
                words[i] += 'ь'
                return

            if currentWord[-2:] == 'ят' and currentWord[:-2] in self.softEndingMasculine:
                words[i] = words[i][:-2] + 'ьт'
                return

            words[i] = words[i] + 'ъ'


    def checkUs(self, i, words, currentWord):
        '''
        Place (big) yus vowels in their ethymological places
        '''

        if currentWord == 'са':
            words[i] = 'сѫ'
            return

        if 'ъ' not in currentWord: return
        if any(x in currentWord for x in self.usExcl):
            return

        if currentWord in self.usHomographs:
            words[i] = words[i].replace('ъ', 'ѫ', 1)
            return

        for root, hasRoot in ((x, x in currentWord) for x in self.usRoots):
            if hasRoot:

                usIndex = currentWord.index(root)

                if root in self.usSecondVowel: usIndex=+2

                if root in self.usHomographs and currentWord.endswith(root): return

                words[i] = words[i][:usIndex] + words[i][usIndex:].replace('ъ', 'ѫ', 1)

                # return

    def checkYat(self, i, words, currentWord, origSentence):
        '''
        Place yat vowels in their ethymological places
        '''

        if 'е' not in currentWord and 'я' not in currentWord: return
        if currentWord in self.yatFullExclusions: return


        if currentWord[-2:] == 'те' and currentWord not in self.yatNotTe:
            addYat = True
            if currentWord in self.verbsHomonymsTe:
                #POS inference
                tagged_words = tag_pos(origSentence)
                # don't add yat to the end of the word if it's a verb
                addYat = not tagged_words[i][1] == 'VERB'

            if addYat:
                words[i] = words[i][:-1] + 'ѣ'

        if currentWord in self.yatFullWords:
            vowel = self.__getYatVowel(currentWord)
            words[i] = words[i].replace(vowel, 'ѣ', 1)
            return

        if currentWord[-3:] in ['еха', 'еше'] and currentWord[-4] not in self.no_succeeding_yat:
            words[i] = words[i][:-3] + 'ѣ' + words[i][-2:]

        for root, hasRoot in ((x, currentWord.startswith(x)) for x in self.yatPrefixes):
            if hasRoot:
                vowel = self.__getYatVowel(root)
                words[i] = words[i].replace(vowel, 'ѣ', 1)

        for root, hasRoot in ((x, x in currentWord) for x in self.yatDoubleRoots):
            if hasRoot:

                yatIndex = currentWord.index(root)
                vowel_first = self.__getYatVowel(root)
                vowel_second = self.__getYatVowel(root.replace(vowel_first, 'X', 1))

                words[i] = words[i][:yatIndex] + words[i][yatIndex:].replace(vowel_first, 'ѣ', 1).replace(vowel_second, 'ѣ', 1)
                return


        if any(x in currentWord for x in self.yatExcl):
            return

        for root, hasRoot in ((x, x in currentWord) for x in self.yatRoots):
            if hasRoot:

                yatIndex = currentWord.index(root)
                vowel = self.__getYatVowel(root)
                words[i] = words[i][:yatIndex] + words[i][yatIndex:].replace(vowel, 'ѣ', 1)
                return


    def checkFeminineThe(self, i, words, currentWord):
        '''
        Place correct ending of feminine words
        '''
        if any(currentWord.endswith(x) for x in self.feminineTheEndings):
            words[i] = words[i][:-2] + 'ь' + words[i][-2:]
            return

        if currentWord.endswith('та') and currentWord[:-2] in self.softEndingFeminine:
            words[i] = words[i][:-2] + 'ьта'


    def checkExclusionWords(self, i, words, currentWord):
        '''
        Change spelling of some words, that had a different spelling
        '''
        for root, hasRoot in ((x, x[0] in currentWord) for x in self.exclusionWords):
            if hasRoot:
                words[i] = words[i].replace(root[0], root[1], 1)
                return



    def convertText(self, text):
        '''
        Convert the words in the text
        '''

        # tokenize by on both sentence and word level
        tokenized = (word_tokenize(s) for s in sent_tokenize(text))

        # idx for the text
        text_idx = 0

        for idx_sentence, s in enumerate(tokenized):
            words = list(map(lambda x: x.lower(), s))
            for i, w in enumerate(s):

                currentWord = words[i]
                self.checkEnding(i, words, currentWord)
                self.checkUs(i, words, currentWord)
                self.checkYat(i, words, currentWord, s)
                self.checkFeminineThe(i, words, currentWord)
                self.checkExclusionWords(i, words, currentWord)

                tmp_index = text_idx + text[text_idx:].index(w)

                text = text[:text_idx] + self.__replaceKeepCase(w, words[i], text[text_idx:])

                text_idx = tmp_index + len(words[i])

        return text
