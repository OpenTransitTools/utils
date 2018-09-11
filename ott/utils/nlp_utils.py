""" Natural Language Processing Utils
    @see https://textblob.readthedocs.io/en/latest/index.html
    @see http://www.nltk.org/
"""

def is_keyword(text_blob, keyword, n=1, s=0):
    """ see if keyword is in the first word (or first n words of the blob)
        :return both t/f for a match, and the index of the word where the match occurred
        @note: depends upon the textblob NLP library for 'spellcheck suggestions and words'
    """
    match = False
    index = -1
    if text_blob:
        for i, word in enumerate(text_blob.words):
            if i < s:  # start the keyword search at index #i
                continue
            if i >= n:  # don't evaluate more than n words deep
                break
            if match is True:
                break

            # test partial matches in this word
            if word.startswith(keyword) or keyword.startswith(word):
                match = True
                index = i
                break

            # test suggested spellings
            suggestions = word.spellcheck()
            for suggestion in suggestions:
                if suggestion[1] > 0.8:
                    if suggestion[0] == keyword.lower():
                        match = True
                        index = i
                        break
    return match, index


def strip(words, s=0, e=None, sp=' '):
    """ assumes words is an array of words (much like what you get from textblob.words """
    # import pdb; pdb.set_trace()
    ret_val = ""
    if e is None or e < 0:
        e = len(words)
    for i, w in enumerate(words):
        if s > i: continue
        if e < i: break
        ret_val = "{}{}{}".format(ret_val, w, sp)
    ret_val = ret_val.rstrip(sp)
    return ret_val
