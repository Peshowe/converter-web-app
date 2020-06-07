## TODO: softEndingWords = softEndingFeminine.union(softEndingMasculine)
#### softEndingFeminine
###     noEndingYat = nouns_in_te + verbse-te
###     Exclusion words as set of tuples
import re
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from .process_vocabs import softEndingMasculine, softEndingFeminine, softEndingWords, yatRoots, yatExcl, usRoots, usExcl, abbreviations, yatNotTe

class Converter():

    cons = {"б", "в", "г", "д", "ж", "з", "к", "л", "м", "н", "п", "р", "с", "т", "ф", "х", "ц", "ч", "ш", "щ"}
    expandedVS = {'във', 'със'}
    usHomographs = {'кът', 'път', 'прът'}
    usSecondVowel = {'гълъб', 'жълъд'}
    yatFullExclusions = {'сте', 'вещ', 'лев', 'лева'}
    yatFullWords = {'ляв', 'лява', 'лявата', 'бях', 'бяха', 'бяхме','вежда', 'вежди', 'веждата', 'веждите', 'де', 'бе'}
    yatDoubleRoots = {'бележ', 'белез', 'белег', 'белех', 'белел', 'беляз', 'белял', 'белях', 'предмет'}
    yatPrefixes = {'пре', 'две', 'ня'}
    feminineTheEndings = {'тта', 'щта'}
    exclusionWords = {('въстава', 'възстава'), ('въстан', 'възстан'), ('нишк', 'нищк'), ('нужни', 'нуждни'), ('овошк', 'овощк'), ('празник', 'праздник'), ('празнич', 'празднич'), ('сърц', 'сърдц'), ('сърчи', 'сърдчи')}
    softEndingMasculine, softEndingFeminine, softEndingWords, yatRoots, yatExcl, usRoots, usExcl, abbreviations, yatNotTe = softEndingMasculine, softEndingFeminine, softEndingWords, yatRoots, yatExcl, usRoots, usExcl, abbreviations, yatNotTe

    def __init__(self, text):

        self.text = text
        # tokenize by on both sentence and word level
        self.tokenized = [word_tokenize(s) for s in sent_tokenize(text)]
        # flatten sentences
        self.words = [w.lower() for s in self.tokenized for w in s ]

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


    def checkEnding(self, i):
        '''
        Place yer vowels at the end of words ending in consonants
        '''
        if self.currentWord[-1] in self.cons:
            if self.currentWord in self.abbreviations:
                return

            if self.currentWord in self.expandedVS:
                self.words[i] = self.words[i][:1] + 'ъ'
                return

            if self.currentWord in self.softEndingWords:
                self.words[i] += 'ь'
                return

            if self.currentWord[-2:] == 'ят' and self.currentWord[:-2] in self.softEndingMasculine:
                self.words[i] = self.words[i][:-2] + 'ьт'
                return

            self.words[i] = self.words[i] + 'ъ'


    def checkUs(self, i):
        '''
        Place (big) yus vowels in their ethymological places
        '''

        if self.currentWord == 'са':
            self.words[i] = 'сѫ'
            return

        if any(x in self.currentWord for x in self.usExcl):
            return

        if self.currentWord in self.usHomographs:
            self.words[i] = self.words[i].replace('ъ', 'ѫ', 1)
            return

        for root, hasRoot in ((x, x in self.currentWord) for x in self.usRoots):
            if hasRoot:

                usIndex = self.currentWord.index(root)

                if root in self.usSecondVowel: usIndex=+2

                if root in self.usHomographs and self.currentWord.endswith(root): return

                self.words[i] = self.words[i][:usIndex] + self.words[i][usIndex:].replace('ъ', 'ѫ', 1)

                return

    def checkYat(self, i):
        '''
        Place yat vowels in their ethymological places
        '''

        if self.currentWord in self.yatFullExclusions: return


        if self.currentWord[-2:] == 'те' and self.currentWord not in self.yatNotTe:
            self.words[i] = self.words[i][:-1] + 'ѣ'

        if self.currentWord in self.yatFullWords:
            vowel = self.__getYatVowel(self.currentWord)
            self.words[i] = self.words[i].replace(vowel, 'ѣ', 1)
            return

        for root, hasRoot in ((x, self.currentWord.startswith(x)) for x in self.yatPrefixes):
            if hasRoot:
                vowel = self.__getYatVowel(root)
                self.words[i] = self.words[i].replace(vowel, 'ѣ', 1)

        for root, hasRoot in ((x, x in self.currentWord) for x in self.yatDoubleRoots):
            if hasRoot:

                yatIndex = self.currentWord.index(root)
                vowel_first = self.__getYatVowel(root)
                vowel_second = self.__getYatVowel(root.replace(vowel_first, 'X', 1))

                self.words[i] = self.words[i][:yatIndex] + self.words[i][yatIndex:].replace(vowel_first, 'ѣ', 1).replace(vowel_second, 'ѣ', 1)
                return


        if any(x in self.currentWord for x in self.yatExcl):
            return

        for root, hasRoot in ((x, x in self.currentWord) for x in self.yatRoots):
            if hasRoot:

                yatIndex = self.currentWord.index(root)
                vowel = self.__getYatVowel(root)
                self.words[i] = self.words[i][:yatIndex] + self.words[i][yatIndex:].replace(vowel, 'ѣ', 1)
                return


    def checkFeminineThe(self, i):
        '''
        Place correct ending of feminine words
        '''
        if any(self.currentWord.endswith(x) for x in self.feminineTheEndings):
            self.words[i] = self.words[i][:-2] + 'ь' + self.words[i][-2:]
            return

        if self.currentWord.endswith('та') and self.currentWord[:-2] in self.softEndingFeminine:
            self.words[i] = self.words[i][:-2] + 'ьта'


    def checkExclusionWords(self, i):
        '''
        Change spelling of some words, that had a different spelling
        '''
        for root, hasRoot in ((x, x[0] in self.currentWord) for x in self.exclusionWords):
            if hasRoot:
                self.words[i] = self.words[i].replace(root[0], root[1], 1)
                return



    def convertWords(self):

        # idx for self.words list
        i = 0

        # idx for the text
        text_idx = 0

        for idx_sentence, s in enumerate(self.tokenized):
            for idx_word, w in enumerate(s):

                self.currentWord = self.words[i]
                self.checkEnding(i)
                self.checkUs(i)
                self.checkYat(i)
                self.checkFeminineThe(i)
                self.checkExclusionWords(i)

                tmp_index = text_idx + self.text[text_idx:].index(w)

                self.text = self.text[:text_idx] + self.__replaceKeepCase(w, self.words[i], self.text[text_idx:])

                text_idx = tmp_index + len(self.words[i])

                # print(f'{w}: {self.words[i]}')

                i+=1
