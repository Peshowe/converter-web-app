"""Read in and define the word lists that help when coverting
"""

import pandas as pd
from pathlib import Path
import os

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
STATIC_DIR = os.path.join(FILE_DIR, "static/converter")
STATIC_DIR = Path(STATIC_DIR)

nouns_in_te = pd.read_csv(
    Path(f"{STATIC_DIR}/word_lists/nouns_in_te.txt"), sep="\n", header=None
)[0].values
verbs_te = pd.read_csv(
    Path(f"{STATIC_DIR}/word_lists/verbs-te.txt"), sep="\n", header=None
)[0].values
verbs_homonyms = pd.read_csv(
    f"{STATIC_DIR}/word_lists/verbs_only_homonyms.txt", sep="\n", header=None
)
softEndingMasculine = set(
    pd.read_csv(
        Path(f"{STATIC_DIR}/word_lists/masculine_soft_ending.txt"),
        sep="\n",
        header=None,
    )[0].values
)
softEndingFeminine = set(
    pd.read_csv(
        Path(f"{STATIC_DIR}/word_lists/feminine_soft_ending.txt"), sep="\n", header=None
    )[0].values
)
yatRoots = set(
    pd.read_csv(f"{STATIC_DIR}/word_lists/yatRoots.txt", sep="\n", header=None)[
        0
    ].values
)
yatExcl = set(
    pd.read_csv(f"{STATIC_DIR}/word_lists/yatExclusions.txt", sep="\n", header=None)[
        0
    ].values
)
usRoots = set(
    pd.read_csv(f"{STATIC_DIR}/word_lists/usRoots.txt", sep="\n", header=None)[0].values
)
usExcl = set(
    pd.read_csv(f"{STATIC_DIR}/word_lists/usExclusions.txt", sep="\n", header=None)[
        0
    ].values
)
abbreviations = set(
    pd.read_csv(f"{STATIC_DIR}/word_lists/abbreviations.txt", sep="\n", header=None)[
        0
    ].values
)


# these ending in "-те" could be verbs or non-verbs
verbsHomonymsTe = set(
    verbs_homonyms[verbs_homonyms[0].apply(lambda x: x.endswith("те"))][0].values
)

# these ending in "-те" are always verbs
yatNotTe = (set(nouns_in_te).union(set(verbs_te))).difference(verbsHomonymsTe)

softEndingWords = softEndingMasculine.union(softEndingFeminine)


cons = {
    "б",
    "в",
    "г",
    "д",
    "ж",
    "з",
    "к",
    "л",
    "м",
    "н",
    "п",
    "р",
    "с",
    "т",
    "ф",
    "х",
    "ц",
    "ч",
    "ш",
    "щ",
}
vowels = {"а", "ъ", "о", "у", "е", "и", "ѣ", "ѫ"}
no_succeeding_yat = vowels.union(
    {"ч", "ш", "ж", "г", "к", "х"}
)  # letters after which we can't have a yat vowel
expandedVS = {"във", "със"}
usHomographs = {"кът", "път", "прът"}
usSecondVowel = {"гълъб", "жълъд"}
yatFullExclusions = {"сте", "вещ", "лев", "лева", "свет", "нея"}
yatFullWords = {
    "ляв",
    "лява",
    "лявата",
    "бях",
    "бяха",
    "бяхме",
    "вежда",
    "вежди",
    "веждата",
    "веждите",
    "де",
    "бе",
    "дето",
    "утре",
}
yatDoubleRoots = {
    "бележ",
    "белез",
    "белег",
    "белех",
    "белел",
    "беляз",
    "белял",
    "белях",
    "предмет",
}
yatPrefixes = {"пре", "две", "ня", "нався"}
yatSuffixes = {"еше", "еха"}
feminineTheEndings = {"тта", "щта"}
exclusionWords = {
    ("въстава", "възстава"),
    ("въстан", "възстан"),
    ("нишк", "нищк"),
    ("нужни", "нуждни"),
    ("овошк", "овощк"),
    ("празник", "праздник"),
    ("празнич", "празднич"),
    ("сърц", "сърдц"),
    ("сърчи", "сърдчи"),
}

usNotExcl = {"откъсн"}

noYatVerbs = {"клех", "взех", "клях", "взях"}


# read in the most frequently used words in the Bulgarian language (scraped from a set of various literature books)
freq_df = pd.read_csv(f"{STATIC_DIR}/word_lists/most_freq.txt", sep="\t", header=None)
freq_df.rename(columns={0: "freq", 1: "word"}, inplace=True)
freq_df = freq_df[~freq_df["word"].isin(verbsHomonymsTe)]
