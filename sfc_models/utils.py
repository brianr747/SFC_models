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

import sys
import tokenize
import keyword
import math
from tokenize import untokenize, NAME
from io import BytesIO


is_python_3 = sys.version_info[0] == 3

if is_python_3:
    import builtins
else:  # pragma: no cover
    import __builtin__

class LogicError(ValueError):
    """
    Throw this when code logic is broken.
    """
    pass


def list_tokens(s):
    """
    Return a list of all NAME tokens (which can be variables, or function names) in a string.

    >>> list_tokens('x = foo + cat()')
    ['x', 'foo', 'cat']

    >>> list_tokens('2 + 3')
    []

    :param s: str
    :return: list
    """
    result = []
    if is_python_3:
        g = tokenize.tokenize(BytesIO(s.encode('utf-8')).readline)  # tokenize the string
        for toknum, tokval, _, _, _ in g:
            if toknum == NAME:  # find NAME tokens
                result.append(tokval)
    else:  # pragma: no cover   [Do my coverage on Python 3]
        g = tokenize.generate_tokens(BytesIO(s.encode('utf-8')).readline)  # tokenize the string
        for toknum, tokval, _, _, _ in g:
            if toknum == NAME:  # find NAME tokens
                result.append(tokval)
    return result

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
    if is_python_3:
        g = tokenize.tokenize(BytesIO(s.encode('utf-8')).readline)  # tokenize the string
        for toknum, tokval, _, _, _ in g:
            if toknum == NAME and tokval == target:  # replace NAME tokens
                result.append((NAME, replacement))
            else:
                result.append((toknum, tokval))
        return untokenize(result).decode('utf-8')
    else:  # pragma: no cover   [Do my coverage on Python 3]
        g = tokenize.generate_tokens(BytesIO(s.encode('utf-8')).readline)  # tokenize the string
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
    if is_python_3:
        g = tokenize.tokenize(BytesIO(s.encode('utf-8')).readline)  # tokenize the string
        for toknum, tokval, _, _, _ in g:
            if toknum == NAME and tokval in lookup:  # replace NAME tokens
                result.append((NAME, lookup[tokval]))
            else:
                result.append((toknum, tokval))
        return untokenize(result).decode('utf-8')
    else:  # pragma: no cover   [Do my coverage on Python 3]
        g = tokenize.generate_tokens(BytesIO(s.encode('utf-8')).readline)  # tokenize the string
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


def get_invalid_variable_names():
    """
    Get a list of invalid variable names for use in sfc_model equations.

    Includes mathematical operators in module 'math'.

    :return: list
    """
    internal = ['self', 'None']
    kw = keyword.kwlist
    if is_python_3:
        built = dir(builtins)
    else:  # pragma: no cover
        built = dir(__builtin__)
    out = internal + kw + built + dir(math)
    # Add back in mathematical operators
    excludes = {'min', 'max', 'pow', 'abs', 'round', 'sum', 'float'}
    out = (x for x in out if x not in excludes)
    return list(out)


class EquationParser(object):
    def __init__(self):
        """
        Equation parsing object. Takes a multi-line string of equations, and turns into blocks
        of variable names, and right-hand side of equations.

        Also includes variable checking, and simplification modifications (to aid convergence).
        """
        self.Endogenous = []
        self.Lagged = []
        self.Exogenous = []
        self.Decoration = []
        self.InitialConditions = {}
        self.AllEquations = {}
        self.Tokens = {}
        self.MaxTime = 0
        self.Err_Tolerance = '.001'

    def ParseString(self, equation_string):
        """
        Parses equations, and breaks them up into logical blocks. All comment information is lost.

        Returns a string with warning information.

        By default, always adds the variables 't' and 'lag_t' as a time axis, unless the user specifies an
        equation for those variables.

        :param equation_string: str
        :return: str
        """
        msg = ''
        self.Endogenous = []
        self.Lagged = []
        self.Exogenous = []
        self.Decoration = []
        self.AllEquations = {}
        self.InitialConditions = {}
        self.Tokens = {}
        self.MaxTime = 0
        self.Err_Tolerance = '.001'
        equation_list = equation_string.split('\n')
        mode = 'endogenous'
        found_t = False
        for equation in equation_list:
            # Any usage of 'exogenous' switches over to the Exogenous block
            # I could skip this, but would need to use eval(), which is dangerous with
            # untrusted inputs.
            if 'exogenous' in equation.lower():
                mode = 'exogenous'
                continue
            # Remove comments (like this one!)
            pos = equation.find('#')
            if pos > -1:
                equation = equation[0:pos]
            equation = equation.strip()
            if len(equation) == 0:
                continue
            splitted = equation.split('=')
            if len(splitted) < 2:
                msg += 'Ignored line: "%s"\n' % (splitted[0],)
                continue
            if len(splitted) > 2:
                msg += 'Line with multiple "=" - ignored: "%s"\n' % (equation,)
                continue
            varname = splitted[0].strip()
            eqn = splitted[1].strip()
            self.AllEquations[varname] = eqn
            if varname == 'MaxTime':
                try:
                    self.MaxTime = int(eqn)
                except ValueError:
                    raise ValueError('Invalid MaxTime value = ' + eqn)
                continue  # pragma: no cover   -- Seems to be a bug in the coverage report on this line...
            if varname == 'Err_Tolerance':
                try:
                    err_tol = float(eqn)
                except ValueError:
                    raise ValueError('Invalid Err_Tolerance value = ' + eqn)
                # We save Err_Tolerance as a string.
                self.Err_Tolerance = eqn
                continue  # pragma: no cover   -- Seems to be a bug in the coverage report on this line...
            if varname in ('t', 't_minus_1'):
                found_t = True
            if mode == 'endogenous':
                # Remove initial conditions equations
                if '(0)' in varname:
                    varname = varname.replace('(0)', '')
                    self.InitialConditions[varname] = eqn
                    continue
                eqn = eqn.replace('(t-1)', '(k-1)')
                eqn = eqn.replace(' (k -1 )', '(k-1)')
                pos = eqn.find('(k-1)')
                if pos == -1:
                    self.Endogenous.append((varname, eqn))
                else:
                    self.Lagged.append((varname, eqn[0:pos]))
            else:
                self.Exogenous.append((varname, eqn))
        if not found_t:
            self.Endogenous.append(('t', 't_minus_1 + 1.0'))
            self.Lagged.append(('t_minus_1', 't'))
            self.AllEquations['t'] = 't_minus_1 + 1.0'
        return msg

    def DumpEquations(self):
        """
        Used for logging
        :return: str
        """
        out = ''
        for varname, rhs in self.Endogenous:
            out += '{0} = {1}\n'.format(varname, rhs)
        for varname, rhs in self.Lagged:
            out += '{0} = {1}(k-1)\n'.format(varname, rhs)
        for varname, rhs in self.Exogenous:
            out += '{0} = {1}\n'.format(varname, rhs)
        return out

    def GenerateTokenList(self):
        """
        Generate the tokens in all equations, puts then into a dictionary (with the variable as key).

        >>> p = EquationParser()
        >>> p.ParseString('x = y + 2*z')
        ''
        >>> p.GenerateTokenList()
        >>> p.Tokens['x']
        ['y', 'z']


        :return: None
        """
        for var in self.AllEquations:
            eq = self.AllEquations[var]
            self.Tokens[var] = list_tokens(eq)

    def ValidateInputs(self):
        """
        Are the equations valid? Currently, only looks for reserved words, and built-in names.

        >>> p = EquationParser()
        >>> p.ParseString('yield = .05')
        ''
        >>> p.ValidateInputs()
        Traceback (most recent call last):
        ...
        NameError: Cannot use variable name: yield, as it is reserved. Call sfc_models.utils.get_invalid_variable_names() to get full list.

        >>> p = EquationParser()
        >>> p.ParseString('inc = 2 * import')
        ''
        >>> p.ValidateInputs()
        Traceback (most recent call last):
        ...
        NameError: Cannot use variable name: import, as it is reserved. Call sfc_models.utils.get_invalid_variable_names() to get full list.


        :return: None
        """
        bad_list = get_invalid_variable_names()
        self.GenerateTokenList()
        for var in self.AllEquations:
            if var in bad_list:
                raise NameError('Cannot use variable name: ' + var + ', as it is reserved. Call sfc_models.utils.get_invalid_variable_names() to get full list.')
            for tok in self.Tokens[var]:
                if tok in bad_list:
                    msg = 'Cannot use variable name: ' + tok + ', as it is reserved. Call sfc_models.utils.get_invalid_variable_names() to get full list.'
                    raise NameError(msg)

    def EquationReduction(self):
        """
        Reduces the difficulty of equations by reducing the number of "non-decorative" endogenous variables.

        :return: None
        """
        num_moved = 1
        while num_moved > 0:
            self.FindExactMatches()
            num_moved = self.MoveDecorative()

    @staticmethod
    def CleanupRightHandSide(s):
        """
        Remove spaces, leading +

        >>> EquationParser.CleanupRightHandSide(' +x')
        'x'

        :return: str
        """
        s = s.strip()
        if len(s) == 0:
            return s
        if s[0] == '+':
            s = s[1:]
        return s

    def FindExactMatches(self):
        """
        Find cases where one variable is defined to equal another variable. Replace all usages the first variable by the
        second equations, making the first decorative.

        >>> p = EquationParser()
        >>> p.ParseString('x = t\\nt = z*1\\nz=x+1')
        ''
        >>> p.Endogenous
        [('x', 't'), ('t', 'z*1'), ('z', 'x+1')]
        >>> p.GenerateTokenList()
        >>> p.FindExactMatches()
        >>> p.Endogenous  # Instead of z = x, we short-circuit to z=t+1
        [('x', 't'), ('t', 'z*1'), ('z', 't+1')]
        >>> # this means that x is now decorative
        >>> p.MoveDecorative()
        1
        >>> p.Decoration
        [('x', 't')]


        The user must avoid creating loops of equality statements; the system will not converge, as it is heavily
        under-determined.

        >>> p = EquationParser()
        >>> p.ParseString('x = t\\nt = x')
        ''
        >>> p.Endogenous
        [('x', 't'), ('t', 'x')]
        >>> p.GenerateTokenList()
        >>> p.FindExactMatches()
        Traceback (most recent call last):
        ...
        ValueError: Equality loop between t and x

        :return: None
        """
        for var, eqn in self.Endogenous:
            rhs = self.CleanupRightHandSide(eqn)
            if rhs in self.AllEquations:
                # We have a case where VAR1 = VAR2.  Replace occurrences of VAR1 by VAR2 in all equations.
                # BUT: Must break loops like:  (x=y), (y=x), since they will not converge
                if var == self.CleanupRightHandSide(self.AllEquations[rhs]):
                    raise ValueError('Equality loop between ' + rhs + ' and ' + var)
                for other in self.AllEquations:
                    self.AllEquations[other] = replace_token(self.AllEquations[other], var, rhs).replace(' ', '')
                    self.Tokens[other] = list_tokens(self.AllEquations[other])
        self.RebuildEquations()

    def RebuildEquations(self):
        """
        Replace endogenous equations from the AllEquations dict.

        :return: None
        """
        new_endo = [(x[0], self.AllEquations[x[0]]) for x in self.Endogenous]
        self.Endogenous = new_endo



    def MoveDecorative(self):
        """
        Move endogenous variables to the "decorative" category if there is no dependence upon them.
        Returns the number of variables moved.
        :return: int

        >>> p = EquationParser()
        >>> eq = 'x=t+1\\ny=4*x\\nt=5'
        >>> p.ParseString(eq)
        ''
        >>> p.Endogenous
        [('x', 't+1'), ('y', '4*x'), ('t', '5')]
        >>> p.GenerateTokenList()  # Need to run before MoveDecorative()
        >>> # We see that neither x or t depend upon y.
        >>> p.MoveDecorative()  # Returns 1 since 1 variable was moved...
        1
        >>> p.Decoration
        [('y', '4*x')]
        >>> p.Endogenous
        [('x', 't+1'), ('t', '5')]
        """
        # Create a copy of the original list.
        working_list = self.Endogenous[:]
        num_found = 0
        for var, old_eqn in working_list:
            found = False
            for other_var in self.Tokens:
                if var in self.Tokens[other_var]:
                    found = True
                    break
            if not found:
                num_found += 1
                self.Decoration.append((var, old_eqn))
                self.Endogenous.remove((var, old_eqn))
        return num_found






