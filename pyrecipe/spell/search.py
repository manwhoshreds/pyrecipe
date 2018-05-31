import re
from collections import Counter
from pyrecipe.db import get_data

class SpellChecker:
    """Check the spelling of a word."""
    
    def __init__(self):
        self.words = []
        _words = get_data()['recipe_names']
        for word in _words:
            self.words += word.split()
        self.words = Counter(self.words)

    def P(self, word): 
        "Probability of `word`."
        return self.words[word] / sum(self.words.values())

    def check(self, word): 
        "Most probable spelling correction for word."
        return max(self.candidates(word), key=self.P)

    def candidates(self, word): 
        "Generate possible spelling corrections for word."
        return (self.known([word]) or self.known(self.edits1(word)) or self.known(self.edits2(word)) or [word])

    def known(self, words): 
        "The subset of words that appear in the dictionary of words."
        return set(w for w in words if w in self.words)

    def edits1(self, word):
        "All edits that are one edit away from `word`."
        letters    = 'abcdefghijklmnopqrstuvwxyz'
        splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
        deletes    = [L + R[1:]               for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
        inserts    = [L + c + R               for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edits2(self, word): 
        "All edits that are two edits away from `word`."
        return (e2 for e1 in self.edits1(word) for e2 in self.edits1(e1))

def spell_check(word):
    spell_checker = SpellChecker()
    check = spell_checker.check(word)
    return check

if __name__ == '__main__':
    test = spell_check('chikeen')
    print(test)



