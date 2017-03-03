"""
base_solver.py

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


class BaseSolver(object):
    def __init__(self, variable_list):
        self.VariableList = variable_list

    def WriteCSV(self, f_name):  # pragma: no cover
        out = self.CreateCsvString()
        with open(f_name, 'w') as f:
            f.write(out)

    def CreateCsvString(self):
        varlist = self.VariableList
        if 't' in varlist:
            varlist.remove('t')
            varlist = ['t', ] + varlist
        out = '\t'.join(varlist) + '\n'
        for i in range(0, len(getattr(self, varlist[0]))):
            txt = []
            for v in varlist:
                txt.append(str(getattr(self, v)[i]))
            out += '\t'.join(txt) + '\n'
        return out
