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

import keyword
import math
import os
import sys
import tokenize
from io import BytesIO
from tokenize import untokenize, NAME


is_python_3 = sys.version_info[0] == 3

if is_python_3:
    import builtins
else:  # pragma: no cover
    # noinspection PyUnresolvedReferences
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

    Cannot use 'k', as that is the discrete time axis step variable.

    :return: list
    """
    internal = ['self', 'None', 'k']
    kw = keyword.kwlist
    if is_python_3:
        built = dir(builtins)
    else:  # pragma: no cover
        built = dir(__builtin__)
    out = internal + kw + built + dir(math)
    return list(out)


def get_invalid_tokens():
    """
    Get a list of invalid tokens that can be used inside sfc_model equations.

    :return: list
    """
    internal = ['self', 'None']
    kw = keyword.kwlist
    if is_python_3:
        built = dir(builtins)
    else:  # pragma: no cover
        built = dir(__builtin__)
    out = internal + kw + built
    # Need to add back in some semi-mathematical operations
    good_tokens = ('float', 'max', 'min', 'sum', 'pow', 'abs', 'round', 'pow')
    out = (x for x in out if x not in good_tokens)
    return list(out)


class Logger(object):
    """
    Class to handle logging.

    Just use the constructor to write. Logging within code just looks like

    Logger("hello!")

    Logger("low level debugging", priority=9)

    If the priority > cutoff, ignore. Hence - level 1 are top level comments.

    To switch the file logged to, specify the log='<name>' parameter.
    The <name> is a short code used to identify the file. BY default, it equals
    'log' (main log).

    This allows us to centralise logging and file handling at a high level.
    """

    # Have a single file handle for all Logger objects
    log_file_handles = {}
    priority_cutoff = 10

    def __init__(self, txt, log='log', priority=1, data_to_format=None, endline=True):
        """
        Do a logging message.

        Usual usage:
        Logger('Hello World!')
        This writes "Hello World!" to the default log 'log'.

        We can add low-level logging by adding a priority (higher priority means
        less important. If that makes sense...)
        Logger('Low level message', priority=9)
        In this case, if we set the cutoff below 9 (default=10), the message will
        not be logged.

        We can direct messages to different files by using the log parameter.

        Logger('Start initial conditions calculation', log='init')
        will write the message to the log labelled 'init'.

        To start logging, need to use Logger.register_log() call. If
        a log is not registered, the Logger() call will do nothing.

        :param txt: str
        :param log: str
        :param priority: int
        :param data_to_format: tuple
        :param endline: bool
        """
        try:
            f = Logger.get_handle(log)
        except KeyError:
            # Was not registered, so just eat the message.
            return
        if priority > Logger.priority_cutoff:
            return
        if data_to_format is not None:
            txt = txt.format(*data_to_format)
        if priority < 1:
            priority = 1
        txt = (' ' * (priority-1)) + txt
        # Need to remove empty strings, or txt[-1] barfs
        if len(txt) == 0:
            if endline:
                txt = ' '
            else:
                return
        # Add an endline automatically (unless endline=False).
        if txt[-1] != '\n' and endline:
            txt += '\n'
        f.write(txt)

    @staticmethod
    def register_log(fname, log='log'):
        """
        Register a file for logging. The fname is the full file path to be
        written. The log parameter is the short code used to specify which log file
        is used.

        The file is only created (overwriting previous contents) when the file handle
        is accessed.

        :param fname: str
        :param log: str
        :return: None
        """
        if log in Logger.log_file_handles:
            raise ValueError('Log already registered: ' + log)
        Logger.log_file_handles[log] = fname

    @staticmethod
    def register_standard_logs(base_file_name): # pragma: no cover
        loginfo = {
            'log': base_file_name + '_log.txt',
            'timeseries': base_file_name + '_out.txt',
            'eqn': base_file_name + '_eqn.txt',
            'step': base_file_name + '_iteration.txt',
            'equilibrium_0': base_file_name + '_equilib.txt',
        }
        for logname in loginfo:
            try:
                Logger.register_log(loginfo[logname], log=logname)
            except ValueError:
                # If already registered, eat the error.
                pass

    @staticmethod
    def get_handle(log='log'):  # pragma: no cover
        """
        Get the file handle associated with the log.

        If the file was not yet opened, it is opened for writing.

        Throws a KeyError if log was not registered.
        :param log: str
        :return:
        """""
        f = Logger.log_file_handles[log]
        if type(f) is str:
            f = open(f, 'w')
            Logger.log_file_handles[log] = f
        return f

    @staticmethod
    def cleanup():
        for k, f in Logger.log_file_handles.items():
            if f is not None:
                if type(f) is not str:
                    f.close()
        Logger.log_file_handles = {}


def get_file_base(fullfile):
    """
    Get the base name of a file
    :param fullfile: str
    :return:
    """
    fname = os.path.basename(fullfile)
    pos = fname.find('.')
    if pos == -1:
        return fname
    else:
        return fname[0:pos]


def register_standard_logs(output_dir, base_file_name): # pragma: no cover
    """
    Convenience function to stick logs in a directory, based base_file_name.

    Typical usage: In examples/scripts, use register_standard_logs('output', __FILE__)
    - Puts the files in the output subdirectory.
    - Uses the code file name (__FILE__) as the base. [The .py will be stripped]

    Operation is operating system safe (as long the output_dir is safe).

    :param output_dir: str
    :param base_file_name: str
    :return:
    """
    base_file_name = os.path.join(output_dir, get_file_base(base_file_name))
    Logger.register_standard_logs(base_file_name)