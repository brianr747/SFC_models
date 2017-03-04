"""
equation.py

Classes to implement equation handling.

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

from sfc_models.utils import LogicError

is_python_3 = sys.version_info[0] == 3


class Term(object):
    """
        Term object; assumed to be simple.

    """
    def __init__(self, term):
        """
        Pass in a string (or possibly another term object), and is parsed.

        :param term: str
        """
        if type(term) == Term:
            self.Constant = term.Constant
            self.Term = term.Term
            self.IsSimple = term.IsSimple
            return
        # Force to be a string; remove whitespace
        term_s = str(term).strip()
        # internal spaces do not matter
        term_s = term_s.replace(' ','')
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
        if is_python_3:
            g = tokenize.tokenize(BytesIO(term_s.encode('utf-8')).readline)  # tokenize the string
        else:  # pragma: no cover   [Do my coverage on Python 3]
            g = tokenize.generate_tokens(BytesIO(term_s.encode('utf-8')).readline)  # tokenize the string
        self.IsSimple = True
        g = tuple(g)
        if len(g) > 3:
            self.IsSimple = False
        else:
            if not g[0][0] == ENCODING: # pragma: no cover
                raise LogicError('Internal error: tokenize behaviour changed')
            if not g[1][0] == NAME:
                self.IsSimple = False
            if not g[2][0] == ENDMARKER: # pragma: no cover
                raise LogicError('Internal error: tokenize behaviour changed')
        self.Term = term_s

    def __str__(self):
        if not self.IsSimple:
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


class Equation(object):
    """
    An equation object
    """
    def __init__(self, lhs, desc = '', rhs=()):
        """
        Create a new equation. Must pass the left hand side (variable name).

        May pass a list of terms; otherwise, starts out empty.
        :param lhs: str
        :param desc: str
        :param rhs: list
        """
        self.LeftHandSide = lhs
        self.Description = desc
        self.TermList = list(rhs)

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
        for other in self.TermList:
            if term.Term == other.Term:
                # Already exists; just add the constants together.
                other.Constant += term.Constant
                return
        # Otherwise, append
        self.TermList.append(term)


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
        Access an equation by the name of the variable on the left hand side.

        Usage
        eqn = equation_block['x']

        :param key: str
        :return: Equation
        """
        return self.Equations[key]



