"""
equation.py

Classes to implement equation handling.

The key class is Equation. It allows us to build up simple equations by adding Term objects.
This is used to create the financial asset and income ('INC') equations.

{Unfortunately being back-fit into code.}

Copyright 2017 Brian Romanchuk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
import tokenize
from io import BytesIO
import copy
from tokenize import untokenize, NAME, ENDMARKER, ENCODING

from sfc_models.utils import LogicError, replace_token_from_lookup

is_python_3 = sys.version_info[0] == 3




class Equation(object):
    """
    An equation object
    """
    def __init__(self, lhs, desc = '', rhs=()):
        """
        Create a new equation. Must pass the left hand side (variable name).

        May pass a list of terms; otherwise, starts out empty.

        May also pass strings as the right hand side; they will be parsed (with limited
        capabilities).

        >>> eq = Equation('x', desc='Variable x', rhs='y+2.')
        >>> print(str(eq))
        x=y+2. # Variable x

        You may even specify the right-hand side in the first variable
        >>> eq2 = Equation('x=z+2')
        >>> print(str(eq2))
        x=z+2

        Additionally, you can append a comment after a '#'
        >>> eq3 = Equation("e = m*c^2 # Einstein's thingy")
        >>> print(str(eq3))
        e=m*c^2 # Einstein's thingy

        :param lhs: str
        :param desc: str
        :param rhs: list
        """
        if '#' in lhs:
            new_lhs, new_desc = lhs.split('#', 1)
            new_desc.replace('#', '')
            new_lhs = new_lhs.strip()
            new_desc = new_desc.strip()
            self.__init__(new_lhs, new_desc, rhs)
            return
        if '=' in lhs:
            lhs, rhs = lhs.split('=', 1)
            lhs = lhs.strip()
            rhs.replace('=', '')
        self.LeftHandSide = lhs
        self.Description = desc
        if type(rhs) == str:
            rhs = Equation.ParseString(rhs)
        self.TermList = []
        for t in rhs:
            self.AddTerm(t)

    def GetRightHandSide(self):
        """
        Returns the string representation of the right hand side.
        :return: str
        """
        out = [str(s) for s in self.TermList]
        out = ''.join(out)
        if out.startswith('+'):
            out = out[1:]
        # If we have no terms, we are equal to zero.
        # This also happens if terms have a Constant = 0
        if out == '':
            out = '0.0'
        return out

    def RHS(self):
        """
        Convenience alias for GetRightHandSide()
        :return: str
        """
        return self.GetRightHandSide()

    def AddTerm(self, term):
        """
        Add a term to the equation. May be a string or Term object.
        :param term: Term
        :return: None
        """
        term = Term(term)
        if len(self.TermList) > 0:
            if term.IsBlob:
                raise LogicError('Cannot add a blob to non-empty equation')
        for other in self.TermList:
            if term.Term == other.Term:
                # Already exists; just add the constants together.
                other.Constant += term.Constant
                return
        # Otherwise, append
        self.TermList.append(term)

    def ReplaceTokensFromLookup(self, lookup):
        """
        Replace tokens based on lookup dict values.
        :param lookup: dict
        :return:
        """
        for t in self.TermList:
            t.ReplaceTokensFromLookup(lookup)

    @staticmethod
    def ParseString(eqn):
        """
        Parse a string, and return a list of Term objects.
        The first Term may be a "blob".
        :param eqn: str
        :return: list
        """
        is_a_term = True
        try:
            t = Term(eqn, is_blob=False)
        except LogicError:
            is_a_term = False
        except SyntaxError:
            is_a_term = False
        except NotImplementedError:
            is_a_term = False
        if is_a_term:
            # Is a single term; no need to parse...
            return [t,]
        return [Term(eqn, is_blob=True)]

    def __str__(self):
        """
        Return the string representatione of the entire equation
        :return: str
        """
        if self.Description == '':
            return '{0}={1}'.format(self.LeftHandSide, self.GetRightHandSide())
        else:
            return '{0}={1} # {2}'.format(self.LeftHandSide, self.GetRightHandSide(), self.Description)


class Term(object):
    """
        Term object; only simple ones are supported by now.

        A simple term consists of a variable name plus a sign. The sign is typically +1. or -1.,
        but if the same variable is added to an equation, the sign is additive.

        May be a "blob," which are complex operations that are left untouched.

        Expected additions:
        [1] Constant term
        [2] one variable times (divided by) another.
    """
    def __init__(self, term, is_blob=False):
        """
        Pass in a string (or possibly another term object), and is parsed.

        If is_blob is True, we do not do any parsing (other than squeezing out internal spaces).

        An equation is allowed one "blob" term, which is the first term. It may be followed
        by non-blob terms.

        As parsing improves, terms can be peeled off of the "blob."

        :param term: str
        :param is_blob: False
        """
        if type(term) == Term:
            self.Constant = term.Constant
            self.Term = term.Term
            self.IsSimple = term.IsSimple
            # Ignore the is_blob input
            self.IsBlob = term.IsBlob
            return
        # Force to be a string; remove whitespace
        term_s = str(term).strip()
        # internal spaces do not matter
        term_s = term_s.replace(' ','')
        if is_blob:
            # If we are a "blob", don't do any parsing.
            self.Constant = 1.0
            self.Term = term_s
            self.IsSimple = True
            self.IsBlob = True
            return
        self.IsBlob = False
        # Rule #1: Eliminate '+' or '-' at front
        self.Constant = 1.0
        if term_s.startswith('+'):
            term_s = term_s[1:]
        elif term_s.startswith('-'):
            self.Constant = -1.0
            term_s = term_s[1:]
        # Rule #2: Allow matched "("
        if term_s.startswith('('):
            if not term_s.endswith(')'):
                raise SyntaxError('Term does not have matching ) - ' + str(term))
            # Remove brackets
            term_s = term_s[1:-1]
            # If we peeled the brackets, remove '+' or '-' again
            if term_s.startswith('+'):
                term_s = term_s[1:]
            elif term_s.startswith('-'):
                # Flip the sign
                self.Constant *= -1.0
                term_s = term_s[1:]
        # We now cannot have embedded '+' or '-' signs.
        if  '+' in term_s:
            raise LogicError('Term cannot contain interior "+" :' + str(term))
        if '-' in term_s:
            raise LogicError('Term cannot contain interior "-" :' + str(term))
        # Do we consist of anything besides a single name token?
        # If so, we are not simple.
        # (Will eventually allow for things like '2*x'.)
        if len(term_s) == 0:
            raise LogicError('Attempting to create an empty term object.')
        if is_python_3:
            g = tokenize.tokenize(BytesIO(term_s.encode('utf-8')).readline)  # tokenize the string
        else:  # pragma: no cover   [Do my coverage on Python 3]
            g = tokenize.generate_tokens(BytesIO(term_s.encode('utf-8')).readline)  # tokenize the string
        self.IsSimple = True
        g = tuple(g)
        if len(g) > 3:
            raise NotImplementedError('Non-simple parsing not done')
            # self.IsSimple = False
        else:
            if not g[0][0] == ENCODING: # pragma: no cover
                raise LogicError('Internal error: tokenize behaviour changed')
            if not g[1][0] == NAME:
                raise NotImplementedError('Non-simple parsing not done')
                # self.IsSimple = False
            if not g[2][0] == ENDMARKER: # pragma: no cover
                raise LogicError('Internal error: tokenize behaviour changed')
        self.Term = term_s

    def __str__(self):
        """
        Convert the Term to a string
        :return: str
        """
        if self.IsBlob:
            return self.Term
        if not self.IsSimple: # pragma: no cover
            raise NotImplementedError('Not dealing with non-simple terms...')
        if self.Constant == 0.0:
            return ''
        if self.Constant == 1.0:
            lead = '+'
        elif self.Constant == -1:
            lead = '-'
        elif self.Constant > 0:
            lead = '+' + str(self.Constant) + '*'
        else:
            lead = str(self.Constant) + '*'
        return lead + self.Term

    def ReplaceTokensFromLookup(self, lookup):
        if self.IsBlob:
            self.Term = replace_token_from_lookup(self.Term, lookup)
            return
        if self.IsSimple:
            if self.Term in lookup:
                self.Term = lookup[self.Term]
            return
        raise NotImplementedError('Need to handle non-simple terms somehow...')



class EquationBlock(object):
    """
    Holds a bloc of equations.

    You can refer to existing equations by using the [] operator.
    """

    def __init__(self):
        self.Equations = {}

    def AddEquation(self, eqn):
        """
        Add an Equation object to the block.
        :param eqn: Equation
        :return: None
        """
        key = eqn.LeftHandSide
        self.Equations[key] = eqn

    def GetEquationList(self):
        """
        Return a sorted list of equations in the block.

        :return: list
        """
        out = list(self.Equations.keys())
        out.sort()
        return out

    def __getitem__(self, key):
        """
        Get an equation by the name of the variable on the left hand side.

        Usage
        eqn = equation_block['x']

        :param key: str
        :return: Equation
        """
        return self.Equations[key]

    def ReplaceTokensFromLookup(self, lookup):
        for eq in self.Equations.values():
            eq.ReplaceTokensFromLookup(lookup)




