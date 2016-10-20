"""
utils.py

Utility functions for the *sfc_models* package.

Copyright 2016 Brian Romanchuk

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

from tokenize import tokenize, untokenize, NAME
from io import BytesIO


class LogicError(ValueError):
    """
    Throw this when code logic is broken.
    """
    pass


def replace_token(s, target, replacement):
    """
    replace_token

    Replaces NAME tokens (variables, functions) in a string (assumed to be equivalent to Python code with a new token.)

    Much safer than string replacement, as it does not hit cases where the target string is a part
    of a different variable (token).

    >>> replace_token('m_x =(x - x_1)', 'x', 'b')
    'm_x =(b -x_1 )'

    >>> replace_token('Little Bunny Foofoo says foo to you', 'foo', 'hello')
    'Little Bunny Foofoo says hello to you '

    Note that the function looks at tokens that could be variables; the contents of strings are not touched.
    >>> replace_token('a = "a fool and his money"', 'a', 'x')
    'x ="a fool and his money"'

    (Note that spacing can be affected, as seen in these examples. Do not rely upon any particular behaviour for
    spaces.)

    :param s: str
    :param target: str
    :param replacement: str
    :return: str
    """
    result = []
    g = tokenize(BytesIO(s.encode('utf-8')).readline)  # tokenize the string
    for toknum, tokval, _, _, _ in g:
        if toknum == NAME and tokval == target:  # replace NAME tokens
            result.append((NAME, replacement))
        else:
            result.append((toknum, tokval))
    return untokenize(result).decode('utf-8')


def replace_token_from_lookup(s, lookup):
    """
    Replace tokens using a lookup dictionary.

    >>> replace_token_from_lookup('y = x', {'y': 'H_y', 'x': 'H_x'})
    'H_y =H_x '

    :param s: str
    :param lookup: dict
    :return: str
    """
    result = []
    g = tokenize(BytesIO(s.encode('utf-8')).readline)  # tokenize the string
    for toknum, tokval, _, _, _ in g:
        if toknum == NAME and tokval in lookup:  # replace NAME tokens
            result.append((NAME, lookup[tokval]))
        else:
            result.append((toknum, tokval))
    return untokenize(result).decode('utf-8')


def create_equation_from_terms(terms):
    """
    Create a string equation (right hand side) from a list of terms.

    >>> create_equation_from_terms(['x','y'])
    'x+y'
    >>> create_equation_from_terms(['-x', 'y', '-z'])
    '-x+y-z'

    :param terms: list
    :return: str
    """
    if len(terms) == 0:
        return ''
    for i in range(0, len(terms)):
        term = terms[i].strip()
        if not term[0] in ('+', '-'):
            term = '+' + term
        terms[i] = term
    if terms[0][0] == '+':
        terms[0] = terms[0].replace('+', '')
    eqn = ''.join(terms)
    return eqn