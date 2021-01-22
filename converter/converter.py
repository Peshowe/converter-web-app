"""Main spelling converter logic
"""

import re
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
import nltk

nltk.download("punkt")

# the function that handles POS tagging
from .pos_tagger import tag_pos

# all the word lists
from .process_vocabs import (
    softEndingMasculine,
    softEndingFeminine,
    softEndingWords,
    yatRoots,
    yatExcl,
    usRoots,
    usExcl,
    abbreviations,
    yatNotTe,
    verbsHomonymsTe,
    cons,
    no_succeeding_yat,
    expandedVS,
    usHomographs,
    usSecondVowel,
    yatFullExclusions,
    yatFullWords,
    yatDoubleRoots,
    yatPrefixes,
    feminineTheEndings,
    exclusionWords,
    usNotExcl,
)


class Converter:
    """Class used to convert words from modern Bulgarian spelling to Ivanchevski spelling"""

    def __init__(self):
        pass

    def __replaceKeepCase(self, word, replacement, text):
        """
        Replace substring, but keep case of original string

        "Borrowed" with some modifications from https://stackoverflow.com/questions/24893977/whats-the-best-way-to-regex-replace-a-string-in-python-but-keep-its-case
        """

        def func(match):
            g = match.group()
            if g.islower():
                return replacement.lower()
            if g.istitle():
                return replacement.title()
            if g.isupper():
                return replacement.upper()
            return replacement

        return re.sub(re.escape(word), func, text, count=1, flags=re.I)

    def __getYatVowel(self, word):
        """
        Get the vowel to be changed into yat
        """
        index_e = -1 if "е" not in word else word.index("е")
        index_ya = -1 if "я" not in word else word.index("я")
        if index_ya == -1:
            vowel = "е"
        elif index_e == -1:
            vowel = "я"
        elif index_ya > index_e:
            vowel = "е"
        else:
            vowel = "я"

        return vowel

    def _checkEnding(self, i, words, currentWord):
        """
        Place yer vowels at the end of words ending in consonants
        """
        if currentWord[-1] in cons:
            if currentWord in abbreviations:
                return

            if currentWord in expandedVS:
                words[i] = words[i][:1] + "ъ"
                return

            if currentWord in softEndingWords:
                words[i] += "ь"
                return

            if currentWord[-2:] == "ят" and currentWord[:-2] in softEndingMasculine:
                words[i] = words[i][:-2] + "ьтъ"
                return

            words[i] = words[i] + "ъ"

    def _checkUs(self, i, words, currentWord):
        """
        Place (big) yus vowels in their ethymological places
        """

        if currentWord == "са":
            words[i] = "сѫ"
            return

        if "ъ" not in currentWord:
            return
        if any(x in currentWord for x in usExcl) and not any(
            x in currentWord for x in usNotExcl
        ):
            return

        if currentWord in usHomographs:
            words[i] = words[i].replace("ъ", "ѫ", 1)
            return

        for root, hasRoot in ((x, x in currentWord) for x in usRoots):
            if hasRoot:

                usIndex = currentWord.index(root)

                if root in usSecondVowel:
                    usIndex = +2

                if root in usHomographs and currentWord.endswith(root):
                    return
                words[i] = words[i][:usIndex] + words[i][usIndex:].replace("ъ", "ѫ", 1)

                return

    def _checkYat(self, i, words, currentWord, origSentence):
        """
        Place yat vowels in their ethymological places
        """

        if "е" not in currentWord and "я" not in currentWord:
            return
        if currentWord in yatFullExclusions:
            return

        if currentWord[-2:] == "те" and currentWord not in yatNotTe:
            addYat = True
            if currentWord in verbsHomonymsTe:
                # POS inference
                tagged_words = tag_pos(origSentence)
                # don't add yat to the end of the word if it's a verb
                addYat = not tagged_words[i][1] == "VERB"

            if addYat:
                words[i] = words[i][:-1] + "ѣ"

        if currentWord in yatFullWords:
            vowel = self.__getYatVowel(currentWord)
            words[i] = words[i].replace(vowel, "ѣ", 1)
            return

        if (
            currentWord[-3:] in ["еха", "еше"]
            and len(currentWord)>=4 and currentWord[-4] not in no_succeeding_yat
        ):
            words[i] = words[i][:-3] + "ѣ" + words[i][-2:]

        for root, hasRoot in ((x, currentWord.startswith(x)) for x in yatPrefixes):
            if hasRoot:
                vowel = self.__getYatVowel(root)
                words[i] = words[i].replace(vowel, "ѣ", 1)

        for root, hasRoot in ((x, x in currentWord) for x in yatDoubleRoots):
            if hasRoot:

                yatIndex = currentWord.index(root)
                vowel_first = self.__getYatVowel(root)
                vowel_second = self.__getYatVowel(root.replace(vowel_first, "X", 1))

                words[i] = words[i][:yatIndex] + words[i][yatIndex:].replace(
                    vowel_first, "ѣ", 1
                ).replace(vowel_second, "ѣ", 1)
                return

        if any(x in currentWord for x in yatExcl):
            return

        for root, hasRoot in ((x, x in currentWord) for x in yatRoots):
            if hasRoot:

                yatIndex = currentWord.index(root)
                vowel = self.__getYatVowel(root)
                words[i] = words[i][:yatIndex] + words[i][yatIndex:].replace(
                    vowel, "ѣ", 1
                )
                return

    def _checkFeminineThe(self, i, words, currentWord):
        """
        Place correct ending of feminine words
        """
        if any(currentWord.endswith(x) for x in feminineTheEndings):
            words[i] = words[i][:-2] + "ь" + words[i][-2:]
            return

        if currentWord.endswith("та") and currentWord[:-2] in softEndingFeminine:
            words[i] = words[i][:-2] + "ьта"

    def _checkExclusionWords(self, i, words, currentWord):
        """
        Change spelling of some words, that had a different spelling
        """
        for root, hasRoot in ((x, x[0] in currentWord) for x in exclusionWords):
            if hasRoot:
                words[i] = words[i].replace(root[0], root[1], 1)
                return

    def convertText(self, text):
        """Convert the words in the text

        Args:
            text (str): Text input

        Returns:
            str: Converted text output
        """

        # NLTK has a weird way with quotes, so we "sanitize" the input here
        text = re.sub(r'"', "``", text)

        # tokenize by on both sentence and word level
        tokenized = (word_tokenize(s) for s in sent_tokenize(text))

        # idx for the text
        text_idx = 0

        # for each word in each sentence, run the spelling conversions
        for idx_sentence, s in enumerate(tokenized):
            words = list(map(lambda x: x.lower(), s))
            for i, w in enumerate(s):

                currentWord = words[i]
                self._checkEnding(i, words, currentWord)
                self._checkUs(i, words, currentWord)
                self._checkYat(i, words, currentWord, s)
                self._checkFeminineThe(i, words, currentWord)
                self._checkExclusionWords(i, words, currentWord)

                tmp_index = text_idx + text[text_idx:].index(w)

                text = text[:text_idx] + self.__replaceKeepCase(
                    w, words[i], text[text_idx:]
                )

                text_idx = tmp_index + len(words[i])

        # revert the quotes "sanitization" (potentionally if someone has used the other weird quotes, this will change them to the normal ones)
        text = re.sub(r"``", '"', text)

        return text
