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
    noYatVerbs,
    expandedVS,
    usHomographs,
    usSecondVowel,
    yatFullExclusions,
    yatFullWords,
    yatDoubleRoots,
    yatPrefixes,
    nonYatPrefixRoots,
    feminineTheEndings,
    exclusionWords,
    usNotExcl,
    freq_df,
    verbs_te,
    vowels,
    wordsToSkip,
)


class Converter:
    """Class used to convert words from modern Bulgarian spelling to Ivanchevski spelling"""

    def __init__(self, preload_cache=False):
        """Create a Converter object and optionally fill in its cache

        Args:
            preload_cache (bool, optional): Precompute a cache (memoise) with the most frequent words in the Bulgarian language. Defaults to False.
        """
        self.frequent_words_cache = {}
        if preload_cache:
            for word in freq_df:
                self.frequent_words_cache[word] = self.convertText(word)

        # delete this df, since we no longer need it (the idea here is memory optimisation)
        # del globals()["freq_df"]

        # Memory usage is about 40 MBs, so shouldn't be a big deal
        import sys

        print(
            "Memory usage of cache is {:.2f} MB".format(
                sys.getsizeof(self.frequent_words_cache) / (1024 ** 2)
            )
        )

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

    def __placeYatVowel(self, i, words, currentWord):
        """Place all yat vowels from currentWord in their respective indices in words[i]"""
        while "ѣ" in currentWord:
            yatIndex = currentWord.index("ѣ")
            words[i] = words[i][:yatIndex] + "ѣ" + words[i][yatIndex + 1 :]
            currentWord = currentWord[:yatIndex] + "X" + currentWord[yatIndex + 1 :]

    def _checkEnding(self, i, words, currentWord):
        """
        Place yer vowels at the end of words ending in consonants
        """
        if currentWord[-1] in cons:

            if currentWord in abbreviations:
                # check some other common abbreviations that should not have an ending yer
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

        for root, hasRoot in ((x, x in words[i]) for x in usRoots):
            if hasRoot:

                usIndex = currentWord.index(root)

                if root in usSecondVowel:
                    usIndex = +2

                if root in usHomographs and currentWord.endswith(root):
                    return
                words[i] = words[i][:usIndex] + words[i][usIndex:].replace("ъ", "ѫ", 1)

    def _checkYat(self, i, words, currentWord, origSentence):
        """
        Place yat vowels in their ethymological places
        """

        if "е" not in currentWord and "я" not in currentWord:
            return
        if currentWord in yatFullExclusions:
            return

        # check for the "-те" suffix and try to infer if it needs a yat letter
        if currentWord[-2:] == "те" and currentWord not in yatNotTe:
            addYat = True
            if currentWord in verbsHomonymsTe:
                # POS inference
                tagged_words = tag_pos(origSentence)
                # if the tagger is not initialised, it will return None
                if tagged_words is not None:
                    # don't add yat to the end of the word if it's a verb
                    addYat = not tagged_words[i][1] == "VERB"

            if addYat:
                currentWord = currentWord[:-1] + "ѣ"

        # check if we have a direct 1 to 1 mapping for this word
        if currentWord in yatFullWords:
            vowel = self.__getYatVowel(currentWord)
            currentWord = currentWord.replace(vowel, "ѣ", 1)
            self.__placeYatVowel(i, words, currentWord)
            return

        # the following three if statemets are for verbs in past tense (окончания на глаголи в минало несвършено време)
        if (
            currentWord[-4:] in {"яхме", "ехме", "яхте", "ехте"}
            and len(currentWord) >= 5
            and currentWord[-5] not in no_succeeding_yat
        ):
            if len(currentWord) == 5 or currentWord[-6:-2] not in noYatVerbs:
                currentWord = currentWord[:-4] + "ѣ" + currentWord[-3:]

        elif (
            currentWord[-3:] in {"яха", "еха", "еше"}
            and len(currentWord) >= 4
            and currentWord[-4] not in no_succeeding_yat
        ):
            if len(currentWord) == 4 or currentWord[-5:-1] not in noYatVerbs:
                currentWord = currentWord[:-3] + "ѣ" + currentWord[-2:]

        elif (
            currentWord[-2:] in {"ех", "ях"}
            and len(currentWord) >= 3
            and currentWord[-3] not in no_succeeding_yat
        ):
            if len(currentWord) == 3 or currentWord[-4:] not in noYatVerbs:
                # we have already added the "-ъ" at the end of words[i], so take that in consideration
                currentWord = currentWord[:-2] + "ѣ" + currentWord[-1]

        # check if the word starts with a prefix that should have yat (but before that make sure that it's not part of the nonYatPrefixRoots set)
        if not any(x in currentWord for x in nonYatPrefixRoots):
            for root, hasRoot in ((x, currentWord.startswith(x)) for x in yatPrefixes):
                if hasRoot:
                    vowel = self.__getYatVowel(root)
                    currentWord = currentWord.replace(vowel, "ѣ", 1)

        # check if the word has a root with two yat letters in it
        for root, hasRoot in ((x, x in currentWord) for x in yatDoubleRoots):
            if hasRoot:

                yatIndex = currentWord.index(root)
                vowel_first = self.__getYatVowel(root)
                vowel_second = self.__getYatVowel(root.replace(vowel_first, "X", 1))

                currentWord = currentWord[:yatIndex] + currentWord[yatIndex:].replace(
                    vowel_first, "ѣ", 1
                ).replace(vowel_second, "ѣ", 1)

                self.__placeYatVowel(i, words, currentWord)
                return

        # stop here if word is in list of words that don't have yat in them
        if any(x in currentWord for x in yatExcl):
            self.__placeYatVowel(i, words, currentWord)
            return

        # search for any roots that have yat in them in the word
        for root, hasRoot in ((x, x in currentWord) for x in yatRoots):
            if hasRoot:
                if root == "дете" and currentWord in verbs_te:
                    # quick and dirty fix for a common problem
                    continue
                yatIndex = currentWord.index(root)
                vowel = self.__getYatVowel(root)
                currentWord = currentWord[:yatIndex] + currentWord[yatIndex:].replace(
                    vowel, "ѣ", 1
                )

                self.__placeYatVowel(i, words, currentWord)
                return

        self.__placeYatVowel(i, words, currentWord)

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
        for root, hasRoot in ((x, x[0] in words[i]) for x in exclusionWords):
            if hasRoot:
                words[i] = words[i].replace(root[0], root[1], 1)
                return

    def _wordVerified(self, w, currentWord):
        """Check if the word should go inside the converter at all.
        Some words (like abbreviations) don't have anything for converting, so we can skip them.

        Args:
            w (str): The original word
            currentWord (str): The word in lower case

        Returns:
            bool: Should we perform the spelling convertion checks or not
        """

        if w in wordsToSkip:
            # if the word is part of this exception list, skip it
            return False

        if (
            w.isupper()
            and not any([c in vowels for c in currentWord])
            and len(currentWord) > 1
        ):
            # if the current word is all caps and doesn't have a vowel, it is probably an abbreviation, so skip (i.e. don't "verify")
            return False

        if len(currentWord) == 1 and currentWord not in {"с", "в"}:
            return False

        # word is "verified"
        return True

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

                if words[i] in self.frequent_words_cache:
                    # if the word is in the precomputed cache, use that
                    words[i] = self.frequent_words_cache[words[i]]

                else:
                    # instead do the spelling conversion checks
                    currentWord = words[i]

                    # if the current word is "verified", perform all the conversion checks on it
                    if self._wordVerified(w, currentWord):
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
