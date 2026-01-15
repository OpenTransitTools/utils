#
# fuzzy string diff
# idea: http://blog.nishtahir.com/fuzzy-string-matching-using-cosine-similarity/
# code: https://stackoverflow.com/a/59449963
# other: https://www.sciencedirect.com/science/article/pii/0167642396000081
#
import re
import math
from collections import Counter


WORD_REGEX = re.compile(r'\w+')
    

def get_cosine(word_list1, word_list2):
    """
    compare two lists of words, and return a value between 0.0 and 1.0 (percent)
    indicating how similar the two lists of words (unordered) are to each other
    e.g., "the cat is black" and "is the cat black" would be 1.0
    """
    ret_val = 0.0

    intersection = set(word_list1.keys()) & set(word_list2.keys())
    numerator = sum([word_list1[x] * word_list2[x] for x in intersection])

    sum1 = sum([word_list1[x]**2 for x in word_list1.keys()])
    sum2 = sum([word_list2[x]**2 for x in word_list2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if denominator:
        ret_val = float(numerator) / denominator

    return ret_val


def normalize(words):
    ret_val = []

    def normalize_dirs(word):
        """ note: expects words to be lowercase """
        if len(word) < 3:
            if   word == "n":  word = "north"
            elif word == "s":  word = "south"
            elif word == "e":  word = "east"
            elif word == "w":  word = "west"
            elif word == "ne": word = "northeast"
            elif word == "nw": word = "northwest"
            elif word == "se": word = "southeast"
            elif word == "sw": word = "southwest"
        return word

    for w in words:
        w = w.lower()
        w = normalize_dirs(w)
        ret_val.append(w)
    return ret_val


def text_to_vector(text):
    words = WORD_REGEX.findall(text)
    words = normalize(words)
    ret_val = Counter(words)
    #print(words); print(ret_val)
    return ret_val


def compare(text1, text2, do_print=False):
    #import pdb; pdb.set_trace()
    cosine_result = 0.0
    if text1 and text2:
        vector1 = text_to_vector(text1)
        vector2 = text_to_vector(text2)
        cosine_result = get_cosine(vector1, vector2)
        
        if do_print:
            percent = int(cosine_result * 100)
            print(f"{percent:4}% : {text1} -v- {text2}")

    return cosine_result


def main():
    compare('834 SE Sandy Street', '834 SE Sandy St', True)
    compare('834 SE Sandy Boulevard', '834 SE Sandy Blvd', True)
    compare('834 SE Sandy Blvd', '834 SE Sandy Blvd Apt 2', True)
    compare('834 SE Sandy Boulevard', '834 SE Sandy Blvd Apt 2', True)
    compare('834 SE Sandy Blvd', '834 S.E. Sandy Blvd', True)
    compare('834 SE Sandy Blvd', '834 Southeast Sandy Blvd', True)
    compare('834 SE Lambeert Blvd', '834 SE Sandy Blvd', True)
    compare('834 SE Lambeert St', '834 SE Sandy Blvd', True)
    compare('834 SE Sandy Blvd', '7834 SE Sandy Blvd', True)
    compare('834 SE Sandy Blvd', '834 SE Sandy Blvd Apt 2', True)
    compare('834 SE Sandy Blvd Apt 3', '834 SE Sandy Blvd Apt 2', True)
    compare('834 Southeast Sandy Boulevard', '834 SE Sandy Blvd', True)

    compare('834 Northeast Sandy Ct', '834 SE Sandy Court', True)
    compare('834 South East Mill Court', '834 SE Mill Ct', True)

    #get_result('', ''))


if __name__ == "__main__":
    main()