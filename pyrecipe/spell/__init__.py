from .spell import SpellChecker



def spell_check(word):
    spell_checker = SpellChecker()
    check = spell_checker.check(word)
    return check
