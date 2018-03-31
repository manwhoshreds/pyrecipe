# -*- coding: utf-8 -*-
"""
    pyrecipe.recipe_numbers
    ~~~~~~~~~~~~~~~~~~~~~~~
    The recipe_numbers module handle various task related to numbers,
    fractions, mixed numbers, etc.. as they are applicable to recipes.

    - RecipeNum: Does well with any numbers we are likely to encounter in
                 pyrecipe. Credit for the creation of this class goes to
                 JB0x2D1 oringialy named Mixed and can found at this post:
                 https://codereview.stackexchange.com/questions/35274/mixed-number-fractions-class

    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""

import math
import numbers
import operator
from fractions import Fraction
from decimal import Decimal


class RecipeNum(Fraction):
    """This class implements Fraction, which implements rational numbers."""

        # We're immutable, so use __new__ not __init__
    def __new__(cls, whole=0, numerator=None, denominator=None):
        """Constructs a Rational.

        Takes a string like '-1 2/3' or '1.5', another Rational instance, a
        numerator/denominator pair, a float, or a whole number/numerator/
        denominator set.  If one or more non-zero arguments is negative,
        all are treated as negative and the result is negative.

        General behavior:  whole number + (numerator / denominator)

        Examples
        --------

        >>> RecipeNum(RecipeNum(-1,1,2), RecipeNum(0,1,2), RecipeNum(0,1,2))
        RecipeNum(-2, 1, 2)
        >>> RecipeNum('-1 2/3')
        RecipeNum(-1, 2, 3)
        >>> RecipeNum(10,-8)
        RecipeNum(-1, 1, 4)
        >>> RecipeNum(Fraction(1,7), 5)
        RecipeNum(0, 1, 35)
        >>> RecipeNum(RecipeNum(1, 7), Fraction(2, 3))
        RecipeNum(0, 3, 14)
        >>> RecipeNum(RecipeNum(0, 3, 2), Fraction(2, 3), 2)
        RecipeNum(1, 5, 6)
        >>> RecipeNum('314')
        RecipeNum(314, 0, 1)
        >>> RecipeNum('-35/4')
        RecipeNum(-8, 3, 4)
        >>> RecipeNum('3.1415')
        RecipeNum(3, 283, 2000)
        >>> RecipeNum('-47e-2')
        RecipeNum(0, -47, 100)
        >>> RecipeNum(1.47)
        RecipeNum(1, 2116691824864133, 4503599627370496)
        >>> RecipeNum(2.25)
        RecipeNum(2, 1, 4)
        >>> RecipeNum(Decimal('1.47'))
        RecipeNum(1, 47, 100)
        """
        self = super(RecipeNum, cls).__new__(cls)

        attempt_failed = False
        zerodiv = False
        if denominator is None: #if two arguments or less, pass to Fraction
            try:
                f1 = Fraction(0)
                f2 = Fraction(whole, numerator)
            except ValueError: #Fraction creation from args failed
                attempt_failed = True
                pass
            except ZeroDivisionError:
                #override Fraction ZeroDivisionError with our own
                zerodiv = True
                pass
            if zerodiv:
                raise ZeroDivisionError('RecipeNum(%s, 0)' % whole)
            if attempt_failed:
                #if str, split and pass to Fraction
                if (numerator is None) and isinstance(whole, str):
                    n = whole.split()
                    if (len(n) == 2):
                        try:
                            f1 = Fraction(n[0])
                            f2 = Fraction(n[1])
                            attempt_failed = False
                        except ValueError:
                            #override Fraction ValueError with our own
                            attempt_failed = True
                            pass
                        except ZeroDivisionError:
                            #override Fraction ZeroDivisionError with our own
                            attempt_failed = False
                            zerodiv = True
                            pass
                    else: #split string items != 2 therefore invalid
                        attempt_failed = True
            if attempt_failed:
                raise ValueError('Invalid literal for RecipeNum: %r' %
                                         whole)
            if zerodiv:
                raise ZeroDivisionError('RecipeNum(\'%s\')' % whole)
        elif (isinstance(whole, numbers.Rational) and #three arguments
              isinstance(numerator, numbers.Rational) and
              isinstance(denominator, numbers.Rational)):
            if denominator == 0:
                raise ZeroDivisionError('RecipeNum(%s, %s, 0)' % (whole, numerator))
            f1 = Fraction(whole)
            f2 = Fraction(numerator, denominator)
        else:
            raise TypeError("all three arguments should be "
                            "Rational instances")
        #handle negatives and consolidate terms into numerator/denominator
        if (f1 < 0) and (f2 > 0):
            f2 = -f2 + f1
        elif (f1 > 0) and (f2 < 0):
            f2 += -f1
        else:
            f2 += f1
        self._numerator = f2.numerator
        self._denominator = f2.denominator
        return self

    def __repr__(self):
        """repr(self)"""
        if (self._numerator < 0) and (self.whole !=0):
            return ('RecipeNum(%s, %s, %s)' % (self.whole, -self.fnumerator,
                                           self._denominator))
        else:
            return ('RecipeNum(%s, %s, %s)' % (self.whole, self.fnumerator,
                                           self._denominator))

    def __str__(self):
        """str(self)"""
        if self.fnumerator == 0:
            return str(self.whole)
        elif (self._numerator < 0) and (self.whole != 0):
            return '%s %s/%s' % (self.whole, -self.fnumerator,
                                 self._denominator)
        elif self.whole != 0:
            return '%s %s/%s' % (self.whole, self.fnumerator,
                                 self._denominator)
        else:
            return '%s/%s' % (self.fnumerator, self._denominator)
    
    def __len__(self):
        return len(self.__str__())
    
    def to_fraction(self):
        n = self.fnumerator
        if self.whole != 0:
            if self.whole < 0:
                n *= -1
            n += self.whole * self._denominator
        return Fraction(n, self._denominator)

    def limit_denominator(self, max_denominator=1000000):
        """Closest Fraction to self with denominator at most max_denominator.

        >>> RecipeNum('3.141592653589793').limit_denominator(10)
        RecipeNum(3, 1, 7)
        >>> RecipeNum('3.141592653589793').limit_denominator(100)
        RecipeNum(3, 14, 99)
        >>> RecipeNum(4321, 8765).limit_denominator(10000)
        RecipeNum(0, 4321, 8765)
        """
        return RecipeNum(self.to_fraction().limit_denominator(max_denominator))

    @property
    def numerator(a):
        """Fraction(a).numerator
        e.g. RecipeNum(1,2,3).numerator ==> Fraction(5,2).numerator
        >>> RecipeNum(1,2,3).numerator
        5
        """
        return a._numerator

    @property
    def denominator(a):
        return a._denominator

    @property
    def whole(a):
        """a % 1
        returns the whole number only
        e.g. 10/3 == 3 1/3 .whole ==> 3
        >>> RecipeNum(10,3).whole
        3
        """
        if a._numerator < 0:
            return -(-a._numerator // a._denominator)
        else:
            return a._numerator // a._denominator

    @property
    def fnumerator(a):
        """ returns the fractional portion's numerator.
        >>> RecipeNum('1 3/4').fnumerator
        3
        """
        if a._numerator < 0:
            return -(-a._numerator % a._denominator)
        else:
            return a._numerator % a._denominator

    def _add(a, b):
        """a + b"""
        return RecipeNum(a.numerator * b.denominator +
                     b.numerator * a.denominator,
                     a.denominator * b.denominator)
    __add__, __radd__ = Fraction._operator_fallbacks(_add, operator.add)

    def _sub(a, b):
        """a - b"""
        return RecipeNum(a.numerator * b.denominator -
                        b.numerator * a.denominator,
                        a.denominator * b.denominator)

    __sub__, __rsub__ = Fraction._operator_fallbacks(_sub, operator.sub)

    def _mul(a, b):
        """a * b"""
        return RecipeNum(a.numerator * b.numerator, a.denominator * b.denominator)

    __mul__, __rmul__ = Fraction._operator_fallbacks(_mul, operator.mul)


    def _div(a, b):
        """a / b"""
        return RecipeNum(a.numerator * b.denominator,
                        a.denominator * b.numerator)

    __truediv__, __rtruediv__ = Fraction._operator_fallbacks(_div, operator.truediv)

    def __pow__(a, b):
        """a ** b

        If b is not an integer, the result will be a float or complex
        since roots are generally irrational. If b is an integer, the
        result will be rational.

        """
        if isinstance(b, numbers.Rational):
            if b.denominator == 1:
                return RecipeNum(Fraction(a) ** b)
            else:
                # A fractional power will generally produce an
                # irrational number.
                return float(a) ** float(b)
        else:
            return float(a) ** b

    def __rpow__(b, a):
        """a ** b"""
        if b._denominator == 1 and b._numerator >= 0:
            # If a is an int, keep it that way if possible.
            return a ** b.numerator

        if isinstance(a, numbers.Rational):
            return RecipeNum(a.numerator, a.denominator) ** b

        if b._denominator == 1:
            return a ** b.numerator

        return a ** float(b)

    def __pos__(a):
        """+a: Coerces a subclass instance to Fraction"""
        return RecipeNum(a.numerator, a.denominator)

    def __neg__(a):
        """-a"""
        return RecipeNum(-a.numerator, a.denominator)

    def __abs__(a):
        """abs(a)"""
        return RecipeNum(abs(a.numerator), a.denominator)

    def __trunc__(a):
        """trunc(a)"""
        if a.numerator < 0:
            return -(-a.numerator // a.denominator)
        else:
            return a.numerator // a.denominator

    def __hash__(self):
        """hash(self)"""
        return self.to_fraction().__hash__()

    def __eq__(a, b):
        """a == b"""
        return Fraction(a) == b

    def _richcmp(self, other, op):
        """Helper for comparison operators, for internal use only.

        Implement comparison between a Rational instance `self`, and
        either another Rational instance or a float `other`.  If
        `other` is not a Rational instance or a float, return
        NotImplemented. `op` should be one of the six standard
        comparison operators.

        """
        return self.to_fraction()._richcmp(other, op)

    def __reduce__(self):
        return (self.__class__, (str(self),))

    def __copy__(self):
        if type(self) == RecipeNum:
            return self     # I'm immutable; therefore I am my own clone
        return self.__class__(self.numerator, self.denominator)

    def __deepcopy__(self, memo):
        if type(self) == RecipeNum:
            return self     # My components are also immutable
        return self.__class__(self.numerator, self.denominator)


if __name__ == '__main__':
    import doctest
    test = doctest.testmod()
    if test[0] == 0:
        print('PASSED')

