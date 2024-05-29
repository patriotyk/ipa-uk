"""
This module provides a Python implementation of the IPA phonetic transcription algorithm found
on Wiktionary (https://en.wiktionary.org/wiki/Module:uk-pronunciation)

The module exposes one function `ipa` and two constants, `ACUTE` and `GRAVE`, so you can
add stresses to the words like this: f"Украї{acute}ні"

Where the дж/дз sequences denote two separate sounds instead of a single one, please indicate this by doubling
the second letter: pass віджжи́лий instead of віджи́лий, підззе́мний instead of підзе́мний, etc.
"""

import re
import unicodedata
from typing import List, Dict

__all__ = [
    "AccentIsMissing",
    "ACUTE",
    "GRAVE",
    "ipa",
]

ACUTE = chr(0x301)
GRAVE = chr(0x300)



class AccentIsMissing(ValueError):
    """
    Raised when the provided text is missing an accent (and has more than one syllable)
    """


grave_decomposer = {
    "ѐ": "е" + GRAVE,
    "Ѐ": "Е" + GRAVE,
    "ѝ": "и" + GRAVE,
    "Ѝ": "И" + GRAVE,
}


def decompose_grave(word: str) -> str:
    """
    Decompose precomposed Cyrillic chars with a grave accent.

    Args:
        word (str): The input word.

    Returns:
        str: The modified word with decomposed precomposed Cyrillic chars.

    Examples:
        >>> decompose_grave("ѐЀѝЍ")
        'ѐЀѝЍ'

        >>> decompose_grave("cafѐ")
        'cafѐ'
    """
    pattern = re.compile("[ѐЀѝЍ]")
    return pattern.sub(lambda match: grave_decomposer[match.group(0)], word)


def ipa(text: str, check_accent: bool = False) -> str:
    """
    Returns the IPA transcription of the given word or sentence according to the
    Wikipedia algorithm found here: https://en.wiktionary.org/w/index.php?title=Module:uk-pronunciation&oldid=75596807

    Parameters:
        text (str): the word or the sentence to transcribe
        check_accent (bool): enable mandatory verification for at least one stressed syllable
    Returns:
        phonetic (str): phonetic transcription
    """

    # TODO: f-strings
    vowel_no_i: str = "aɛɪuɔɐoʊe"
    vowel: str = vowel_no_i + "i"
    vowel_c: str = "[" + vowel + "]"
    consonant_no_w: str = "bdzʒɡɦmnlrpftskxʃj"
    consonant_no_w_c: str = "[" + consonant_no_w + "]"
    consonant: str = consonant_no_w + "ʋβ̞wʍ"
    consonant_c: str = "[" + consonant + "]"
    palatalizable: str = "tdsznlrbpʋfɡmkɦxʃʒ"
    palatalizable_c: str = "[" + palatalizable + "]"

    voiced_obstruent: str = r"[bdzʒɡɦ]"
    voicing: Dict[str, str] = {
        r"p": "b",
        r"f": "v",
        r"t": "d",
        r"tʲ": "dʲ",
        r"s": "z",
        r"sʲ": "zʲ",
        r"ʃ": "ʒ",
        r"k": "ɡ",
        r"x": "ɦ",
        r"t͡s": "d͡z",
        r"t͡sʲ": "d͡zʲ",
        r"t͡ʃ": "d͡ʒ",
        r"ʃt͡ʃ": "ʒd͡ʒ",
    }

    perm_syl_onset: set[str] = {
        "spr",
        "str",
        "skr",
        "spl",
        "skl",
        "sp",
        "st",
        "sk",
        "sf",
        "sx",
        "pr",
        "br",
        "tr",
        "dr",
        "kr",
        "gr",
        "ɦr",
        "fr",
        "xr",
        "pl",
        "bl",
        "kl",
        "gl",
        "ɦl",
        "fl",
        "xl",
    }

    # That decompose_grave is probably an obsolete call
    text = decompose_grave(text).lower()

    if check_accent:
        if ACUTE not in text and GRAVE not in text:
            if len(re.findall(r"[аеєиіїоуюя]", text)) > 1:
                raise AccentIsMissing(
                    "The provided text is missing an accent (and has more than one syllable). "
                    "Set check_accent=False to disable that check"
                )

    # convert commas and en/en dashes to IPA foot boundaries
    # text = re.sub(r"\s*[,–—]\s*", " | ", text)

    # canonicalize multiple spaces
    text = re.sub(r"\s+", " ", text)

    phonetic_chars_map: List[Dict[str, str]] = [
        # character sequences of three that map to IPA sounds
        {
            "дзь": "d͡zʲ",
            # Dental plosives assimilate to following hissing/hushing consonants,
            # which is not noted in the spelling.
            "тьс": "t͡sʲː",
        },
        # character sequences of two that map to IPA sounds
        {
            "дж": "d͡ʒ",
            "дз": "d͡z",
            # Dental plosives assimilate to following hissing/hushing consonants,
            # which is not noted in the spelling.
            "дс": "d͡zs",
            "дш": "d͡ʒʃ",
            "дч": "d͡ʒt͡ʃ",
            "дц": "d͡zt͡s",
            "тс": "t͡s",
            "тш": "t͡ʃʃ",
            "тч": "t͡ʃː",
            "тц": "t͡sː",
        },
        # single characters:
        {
            "а": "a",
            "б": "b",
            "в": "ʋ",
            "г": "ɦ",
            "ґ": "ɡ",
            "д": "d",
            "е": "ɛ",
            "є": "jɛ",
            "ж": "ʒ",
            "з": "z",
            "и": "ɪ",
            "і": "i",
            "ї": "ji",
            "й": "j",
            "к": "k",
            "л": "l",
            "м": "m",
            "н": "n",
            "о": "ɔ",
            "п": "p",
            "р": "r",
            "с": "s",
            "т": "t",
            "у": "u",
            "ф": "f",
            "х": "x",
            "ц": "t͡s",
            "ч": "t͡ʃ",
            "ш": "ʃ",
            "щ": "ʃt͡ʃ",
            "ь": "ʲ",
            "ю": "ju",
            "я": "ja",
            "’": "j",
            # stress marks:
            ACUTE: "ˈ",
            GRAVE: "ˌ",
        },
    ]

    orthographic_replacements: dict = {
        # Consonant cluster simplifications that always occur orthographically
        r"нтськ": "ньськ",
        r"стськ": "ськ",
        r"нтст": "нст",
        r"стч": "шч",
        r"стд": "зд",
        r"стс": "сː",
        # hash here is the special character used to mark word boundaries
        r"#зш": "#шː",
        r"зш": "жш",
        r"#зч": "#шч",
        r"зч": "жч",
        # Long consonants that are orthographically geminated
        r"([бвгґд])\1": r"\1ː",
        r"([^д]+)жж": r"\1жː",  # джж sequence encodes diphonemic дж
        r"([^д]+)зз": r"\1зː",  # дзз sequence encodes diphonemic дз
        r"([йклмнпрстфхцчшщ])\1": r"\1ː",
        "дждж": "джː",
        "дздз": "дзː",
    }

    pronuns = []

    # -- FIXME, not completely correct, we need to treat hyphens at beginning and end of
    # -- a word as indicating unstressed pronunciation.

    for phonetic in re.split(r"[\s\-]+", text):
        phonetic = "#" + phonetic + "#"

        for regex, replacement in orthographic_replacements.items():
            phonetic = re.sub(regex, replacement, phonetic)

        # Remap apostrophe to '%' so that it doesn't conflict with IPA stress mark
        phonetic = re.sub("'", "%", phonetic)

        # replace multiple letter sequences
        for replacements in phonetic_chars_map:
            for key, replacement in replacements.items():
                phonetic = re.sub(key, replacement, phonetic)

        # -- move stress mark, added by phonetic_chars_map, before vowel
        phonetic = re.sub(r"([aɛiɪuɔ])([ˈˌ])", r"\2\1", phonetic)

        # add accent if the word is monosyllabic and not allow_unstressed,
        # so that monosyllabic words without explicit stress marks get stressed
        # vowel allophones; we use a different character from the regular
        # primary stress mark so we can later remove it without affecting
        # explicitly user-added accents on monosyllabic words, as in нема́ за́ що.

        # including stress mark for single-syllable words if check_accent is set to true
        number_of_vowels = len(re.findall(r"[aɛiɪuɔ]", phonetic))
        if number_of_vowels == 1 and check_accent:
            phonetic = re.sub(r"([aɛiɪuɔ])", r"⁀\1", phonetic)

        # palatalizable consonants before /i/ or /j/ become palatalized
        phonetic = re.sub(
            r"(" + palatalizable_c + ")([ː]?)([ˈˌ⁀]?)i", r"\1ʲ\2\3i", phonetic
        )
        phonetic = re.sub(r"(" + palatalizable_c + ")([ː]?)j", r"\1ʲ\2", phonetic)

        # eliminate garbage sequences of [ʲːj] resulting from the -тьс- cluster followed by [j]
        phonetic = re.sub(r"ʲːj", r"ʲː", phonetic)

        # consonant simplification: ст + ц' → [с'ц']. We do it here because of palatalization.
        # Due to the т +ц → [ц:] rule length is present. According to Орфоепскі словник p. 13,
        # both forms are proper, without length in normal (colloquial) speech and with length
        # in slow speech.
        phonetic = re.sub(r"st͡sʲ([ː]?)", r"sʲt͡sʲ", phonetic)

        # TODO: probably we need to fall back to the endless loop of ipa function

        for voiceless, voiced in voicing.items():
            phonetic = re.sub(
                voiceless + "(" + voiced_obstruent + "+)", voiced + r"\1", phonetic
            )

        # In the sequence of two consonants, of which the second is soft, the first is pronounced soft too
        # unless the first consonant is a labial, namely б, п, в, ф, м.

        phonetic = re.sub(r"([tdsznl])(.)ʲ", r"\1ʲ\2ʲ", phonetic)
        phonetic = re.sub(r"([tdsznl])t͡sʲ", r"\1ʲt͡sʲ", phonetic)
        phonetic = re.sub(r"([tdsznl])d͡zʲ", r"\1ʲd͡zʲ", phonetic)
        phonetic = re.sub(r"t͡s(.)ʲ", r"t͡sʲ\1ʲ", phonetic)
        phonetic = re.sub(r"d͡z(.)ʲ", r"d͡zʲ\1ʲ", phonetic)
        phonetic = re.sub(r"d͡zt͡sʲ", r"d͡zʲt͡sʲ", phonetic)
        phonetic = re.sub(r"t͡sd͡zʲ", r"t͡sʲd͡zʲ", phonetic)

        # Hushing consonants ж, ч, ш assimilate to the following hissing consonants, giving a long hissing consonant:
        # [ʒ] + [t͡sʲ] → [zʲt͡sʲ], [t͡ʃ] + [t͡sʲ] → [t͡sʲː], [ʃ] + [t͡sʲ] → [sʲt͡sʲ], [ʃ] + [sʲ] → [sʲː]
        phonetic = re.sub(r"ʒt͡sʲ", r"zʲt͡sʲ", phonetic)
        phonetic = re.sub(r"t͡ʃt͡sʲ", r"t͡sʲː", phonetic)
        phonetic = re.sub(r"ʃt͡sʲ", r"sʲt͡sʲ", phonetic)
        phonetic = re.sub(r"ʃsʲ", r"sʲː", phonetic)

        # Hissing consonants before hushing consonants within a word assimilate - on зш and зч word-initially and
        # word-medially see above.
        # [s] + [ʃ] → [ʃː],  [z] + [ʃ] → [ʒʃ], [z] + [t͡ʃ] → [ʒt͡ʃ]
        # [z] + [d͡ʒ] → [ʒd͡ʒ]
        phonetic = re.sub(r"zʒ", r"ʒː", phonetic)
        phonetic = re.sub(r"sʃ", r"ʃː", phonetic)
        phonetic = re.sub(r"zt͡ʃ", r"ʒt͡ʃ", phonetic)
        phonetic = re.sub(r"zd͡ʒ", r"ʒd͡ʒ", phonetic)
        phonetic = re.sub(r"t͡ʒ", r"d͡ʒ", phonetic)
        phonetic = re.sub(r"t͡z", r"d͡z", phonetic)

        # cleanup: excessive palatalization: CʲCʲCʲ → CCʲCʲ
        phonetic = re.sub(
            r"([^aɛiɪuɔ]+)ʲ([^aɛiɪuɔ]+)ʲ([^aɛiɪuɔ]+)ʲ", r"\1\2ʲ\3ʲ", phonetic
        )

        # unstressed /a/ has an allophone [ɐ]
        phonetic = re.sub(r"([^ˈˌ⁀])a", r"\1ɐ", phonetic)
        # unstressed /u/ has an allophone [ʊ]
        phonetic = re.sub(r"([^ˈˌ⁀])u", r"\1ʊ", phonetic)
        # unstressed /ɔ/ has by assimilation an allophone [o] before a stressed syllable with /u/ or /i/
        phonetic = re.sub(r"ɔ([bdzʒɡɦmnlrpftskxʲʃ͡]+)([ˈˌ⁀][uiʊ])", r"o\1\2", phonetic)
        # unstressed /ɛ/ has an allophone /e/
        phonetic = re.sub(r"([^ˈˌ⁀])[ɛ]", r"\1e", phonetic)

        # Remove the monosyllabic stress we auto-added to ensure that vowels in
        # monosyllabic words get stressed allophones. Do this before vocalizing
        # /ʋ/ and /j/. NOTE: Nothing below should depend on stress marks being
        # present.
        phonetic = re.sub(r"⁀", r"", phonetic)

        # /ʋ/ has an allophone [u̯] in a syllable coda
        phonetic = re.sub(
            r"(" + vowel_c + ")ʋ([" + consonant_no_w + "#])", r"\1u̯\2", phonetic
        )
        # /ʋ/ has an allophone [w] before /ɔ, u/ and voiced consonants
        # (not after a vowel; [ʋ] before vowel already converted)
        phonetic = re.sub(r"ʋ([ˈˌ]?[ɔuoʊbdzʒɡɦmnlr])", r"w\1", phonetic)
        # /ʋ/ has an allophone [β̞] before remaining vowels besides /i/
        # Not sure whether this looks good.
        # phonetic = re.sub("ʋ([ˈˌʲ]*[" .. vowel_no_i .. "])", "β̞\1", phonetic)
        # /ʋ/ has an allophone [ʍ] before voiceless consonants (not after a vowel;
        # [ʋ] before vowel already converted)
        phonetic = re.sub(r"ʋ([pftskxʃ])", r"ʍ\1", phonetic)

        # in a syllable-final position (i.e. the first position of a syllable coda) /j/ has an allophone [i̯]:
        phonetic = re.sub(
            r"(" + vowel_c + ")j([" + consonant_no_w + "#])", r"\1i̯\2", phonetic
        )
        # also at the beginning of a word before a consonant
        phonetic = re.sub(r"#j(" + consonant_no_w_c + ")", r"#i̯\1", phonetic)

        # remove old orthographic apostrophe
        phonetic = re.sub(r"%", r"", phonetic)
        # stress mark in correct place
        # (1) Put the stress mark before the final consonant of a cluster (if any).
        phonetic = re.sub(r"([^#" + vowel + "]?[ʲː]*)([ˈˌ])", r"\2\1", phonetic)
        # (2) Continue moving it over the rest of an affricate with a tie bar.
        phonetic = re.sub(r"([^#" + vowel + "]͡)([ˈˌ])", r"\2\1", phonetic)

        # (3) Continue moving it over any "permanent onset" clusters (e.g. st, skr, pl, also Cj).
        def onset_replacement(match):
            a, aj, b, bj, stress, c = match.groups()

            cluster_key = a + b + c
            if cluster_key in perm_syl_onset:
                return stress + a + aj + b + bj + c
            elif (b + c in perm_syl_onset) or (c == "j"):
                return a + aj + stress + b + bj + c
            else:
                return a + aj + b + bj + stress + c

        pattern = re.compile(rf"(.)(ʲ?)({consonant_c})(ʲ?)([ˈˌ])({consonant_c})")
        phonetic = pattern.sub(onset_replacement, phonetic)

        phonetic = re.sub(r"([^#" + vowel + "]͡)([ˈˌ])(.ʲ?j)", r"\2\1\3", phonetic)
        phonetic = re.sub(r"([^#" + vowel + "]͡)([ˈˌ])(.ʲ?)", r"\1\3\2", phonetic)
        # (5) Move back over any remaining consonants at the beginning of a word.
        phonetic = re.sub(r"#([^#" + vowel + "]+)([ˈˌ])", r"#\2\1", phonetic)
        # (6) Move back over u̯ or i̯ at the beginning of a word.
        phonetic = re.sub(r"#([ui]̯)([ˈˌ])", r"#\2\1", phonetic)

        phonetic = re.sub(r"ʲ?ːʲ", r"ʲː", phonetic)

        # use dark [ɫ] for non-palatal /l/
        phonetic = re.sub(r"l([^ʲ])", r"ɫ\1", phonetic)

        pronuns.append(phonetic)

    return " ".join(pronuns).replace("#", "")


if __name__ == "__main__":
    for w in [f"Сла{ACUTE}ва", f"Украї{ACUTE}ні", f"сме{ACUTE}рть", f"ворога{ACUTE}м"]:
        print(w, "->", ipa(w, check_accent=True))
    for w in ["остзе́йці"]:
        print(w, "->", ipa(w, check_accent=True))
