"""
iterative_machine_generator.py

Set up a system of equations, generates the Python module to
solve it.

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

import warnings

template = """
$$$
FNAME

Machine-generated model code
$$$



class SFCModel(object):
    $$$
    Model

    Implements the following system of equations.

<DOC_EQUATIONS>
    $$$
    def __init__(self):
        self.MaxIterations = 100
        self.MaxTime = MAXTIME
        self.T = 0
VAR_DECLARATION

ITERATOR

    def main(self):
        for t in range(0, self.MaxTime):
            self.T = t
            self.RunOneStep()

    def RunOneStep(self):
<PACK_VARS>
        orig_vector = (<ORIG_VECTOR>)
        err = 1.
        cnt = 0
        while err > .001:
            new_vector = self.Iterator(orig_vector)
            err = self.CalcError(orig_vector, new_vector)
            orig_vector = new_vector
            cnt += 1
            if cnt > self.MaxIterations:
                raise ValueError('No Convergence!')
<UNPACK_VARS>

    @staticmethod
    def CalcError(vec1, vec2):
        err = 0.
        for val1, val2 in zip(vec1, vec2):
            err += abs(val1 - val2)
        return err


if __name__ == '__main__':
    obj = SFCModel()
    obj.main()


"""


class IterativeMachineGenerator(object):
    """
    Generate code to solve system.
    """

    def __init__(self, equation_string=''):
        """
        Instantiate object.
        if equation_string is non-empty, automatically parses it using ParseString() to
        generate system of equations.

        :param equation_string: str
        """
        self.Endogenous = []
        self.Lagged = []
        self.Exogenous = []
        self.TIME = [0, ]
        self.AllVariables = []
        self.EquationList = []
        self.FunctionText = ''
        self.MaxIterations = 100
        self.MaxTime = 0
        if len(equation_string) > 0:
            self.ParseString(equation_string)

    def ParseString(self, equation_string):
        """
        Read in a mutliline string to populate variable and equation lists.

        :param equation_string: str
        :return: str
        """
        msg = ''
        equation_list = equation_string.split('\n')
        mode = 'endogenous'
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
            if varname == 'MaxTime':
                try:
                    self.MaxTime = int(eqn)
                except ValueError:
                    raise ValueError('Invalid MaxTime value = ' + eqn)
                continue  # pragma: no cover   -- Seems to be a bug in the coverage report on this line...
            if mode == 'endogenous':
                pos = eqn.find('(t-1)')
                if pos == -1:
                    self.Endogenous.append((varname, eqn))
                else:
                    self.Lagged.append((varname, eqn[0:pos]))
            else:
                self.Exogenous.append((varname, eqn))
        if len(msg) > 0:
            warnings.warn('Could not parse some sections of input. Examine ParseString() output to view issues.',
                          SyntaxWarning)
        return msg

    def main(self, file_name):
        """
        Once the equation information is filled in, call this to generate the file.
        :param file_name: str
        :return:
        """
        self.GenerateEquations()
        self.GenerateFunction()
        self.GenerateFile(file_name)

    def GenerateEquations(self):
        self.EquationList = []
        self.AllVariables = []
        initial_conditions = []
        for variable_name, eqn in self.Endogenous:
            self.AllVariables.append(variable_name)
            self.EquationList.append(eqn)
            initial_conditions.append(0.)
        for variable_name, name_of_var in self.Lagged:
            self.AllVariables.append(variable_name)
            self.EquationList.append(variable_name)
        for variable_name, value in self.Exogenous:
            self.AllVariables.append(variable_name)
            self.EquationList.append(variable_name)

    def GenerateVarDeclaration(self):
        indent = ' ' * 8
        out = ""
        for variable_name, eqn in self.Endogenous:
            # If we have an equation like '0.5', that means we have a fixed parameter.
            # Initialise to that value. We could mark such variables...
            try:
                param_value = float(eqn.strip())
            except ValueError:
                param_value = 0.
            out += indent + 'self.%s = [%f,]\n' % (variable_name, param_value)
        for variable_name, value in self.Exogenous:
            out += indent + "self." + variable_name + ' = ' + value + '\n'
        return out

    def GenerateFunction(self):
        """
        Generate function code based on equation and variable lists
        :return: str
        """
        indent = ' ' * 8
        out = '    def Iterator(self, in_vec):\n'
        # Unpack in_vec
        out += indent + ', '.join(self.AllVariables) + ' = in_vec \n'
        # Create the decorated version of variables
        decorated = ['NEW_' + x for x in self.AllVariables]
        # Insert equations
        for i in range(0, len(self.AllVariables)):
            out += indent + decorated[i] + ' = ' + self.EquationList[i] + '\n'
        # Pack 'em back up
        out += indent + 'return ' + ', '.join(decorated) + '\n'
        self.FunctionText = out
        return out

    def GenerateOrigVector(self):
        varz = ', '.join(self.AllVariables)
        return varz

    def GenerateDocEquations(self):
        out = ['Endogenous variables and parameters\n',
               '===================================\n']
        for var, eqn in self.Endogenous:
            out.append('%s = %s,\n' % (var, eqn))
        out.append('where lagged variables are:\n')
        for variable_name, name_of_var in self.Lagged:
            out.append('%s(t) = %s(t-1)\n' % (variable_name, name_of_var))
        out.append('\n')
        out.append('\n')
        out.append('Exogenous Variables\n')
        out.append('===================\n')
        for variable_name, value in self.Exogenous:
            out.append(variable_name + '\n')
        out = [(' ' * 4) + x for x in out]
        out = ''.join(out)
        return out

    def GeneratePackVars(self):
        indent = ' ' * 8
        out = ''
        for variable_name, eqn in self.Endogenous:
            out += indent + variable_name + ' = self.' + variable_name + '[-1]\n'
        for variable_name, name_of_var in self.Lagged:
            out += indent + variable_name + ' = self.' + name_of_var + '[self.T -1]\n'
        for variable_name, value in self.Exogenous:
            out += indent + variable_name + ' = self.' + variable_name + '[self.T]\n'
        return out

    def GenerateUnpackVars(self):
        indent = ' ' * 8
        out = ''
        cnt = 0
        for variable_name, eqn in self.Endogenous:
            out += indent + '%s = orig_vector[%i]\n' % (variable_name, cnt)
            cnt += 1
            out += indent + 'self.' + variable_name + '.append(' + variable_name + ')\n'
        return out

    def GenerateFile(self, file_name):
        output = template
        output = output.replace('$', '"')
        # MAXTIME
        output = output.replace('MAXTIME', str(self.MaxTime))
        # VAR_DECLARATION
        output = output.replace('VAR_DECLARATION', self.GenerateVarDeclaration())
        # Orig Vector
        output = output.replace('<ORIG_VECTOR>', self.GenerateOrigVector())
        # Pack vars
        output = output.replace('<PACK_VARS>', self.GeneratePackVars())
        # UnPack vars
        output = output.replace('<UNPACK_VARS>', self.GenerateUnpackVars())
        # Doc Equations
        output = output.replace('<DOC_EQUATIONS>', self.GenerateDocEquations())
        # ITERATOR
        output = output.replace('ITERATOR', self.FunctionText)
        with open(file_name, 'w') as f:
            f.write(output)


    @staticmethod
    def CalcError(vec1, vec2):
        err = 0.
        for val1, val2 in zip(vec1, vec2):
            err += abs(val1 - val2)
        return err
