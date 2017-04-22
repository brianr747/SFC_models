"""
extras.py

Plotting class to generate 2-D charts for examples. This file is the only one (other than another example)
that depends upon matplotlib. If matplotlib is not imported (that is, not installed), does
a fall back operation (dump to console, and eventually, a csv). The user can either find a plotting
function that works, or import the csv data.

I have isolated this so that it is possible to run examples with no external dependencies.

To install matplotlib, running "pip install matplotlib" in the approppriate Python "Scripts" directory
should do the job. Unfortunately, it can sometimes fail. There is up-to-date documentation on the internet;
I do not want to attempt to cover the details here.

This nodule is largely uncovered by unit tests, as it is interactive. It should be moved elsewhere, but
putting it within sfc_models makes installation instructions simpler. (Users will still need to install matlibplot,
which can be a tricky install.)

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

from pprint import pprint
import os

try:
    import matplotlib.pyplot as plt
except ImportError:  # pragma: no cover
    pprint("Unable to load matplotlib; no graphing output is possible!")
    plt = None


class Quick2DPlotParams(object):
    OutputDirectory = None
    dpi = 90
    ParamFileName = 'Quick2DPlot_params.txt'
    FileRead = False
    FontSize = 11
    Width = 4.5
    Height = 3

    def ReadFile(self):  # pragma: no cover
        # If we have already read the file, do not do it again.
        if self.FileRead:
            return
        self.FileRead = True
        if not os.path.isfile(self.ParamFileName):
            return
        f = open(self.ParamFileName, 'r')
        for row in f:
            data = row.split('=')
            if len(data) != 2:
                continue
            param, val = data
            param = param.strip()
            val = val.strip()
            param = param.lower()
            if param == 'dpi':
                self.dpi = int(val)
            if param == 'output_directory':
                self.OutputDirectory = val
            if param == 'width':
                self.Width = float(val)
            if param == 'height':
                self.Height = float(val)
            if param == 'fontsize':
                self.FontSize = float(val)


class Quick2DPlot(object):
    def __init__(self, x, y, title='', run_now=True, output_directory=None, filename=None):
        self.X = x
        self.Y = y
        self.Title = title
        self.XLabel = None
        self.YLabel = None
        self.Legend = None
        self.FileName = filename
        self.LegendPos = 'best'
        self.OutputDirectory = output_directory
        if run_now:
            self.DoPlot()

    def DoPlot(self):  # pragma: no cover
        if plt is None:
            pprint('Attempted to plot the following data; cannot to do because cannot import matplotlib')
            if type(self.X[0]) == list:
                pprint('Series 1')
                pprint('%s %20s' % ('X', 'Y'))
                for i in range(0, len(self.X[0])):
                    pprint('%f %20f' % (self.X[0][i], self.Y[0][i]))
                pprint('Series 2')
                pprint('%s %20s' % ('X', 'Y'))
                for i in range(0, len(self.X[1])):
                    pprint('%f %20f' % (self.X[1][i], self.Y[1][i]))
            else:
                pprint('%s %20s' % ('X', 'Y'))
                for i in range(0, len(self.X)):
                    pprint('%f %20f' % (self.X[i], self.Y[i]))
            return
        if type(self.X[0]) == list:
            fig, ax = plt.subplots()
            ax.plot(self.X[0], self.Y[0], marker='o', markersize=4)
            ax.plot(self.X[1], self.Y[1], marker='^', markersize=4.5)
            # plt.plot(self.X[0], self.Y[0], self.X[1], self.Y[1], marker='o')
        else:
            plt.plot(self.X, self.Y, marker='o')
        params = Quick2DPlotParams()
        params.ReadFile()
        plt.rcParams.update({'font.size': params.FontSize})
        figure = plt.gcf()
        figure.set_size_inches(4.5, 3)
        if len(self.Title) > 0:
            plt.title(self.Title)
        plt.grid()
        if self.XLabel is not None:
            plt.xlabel(self.XLabel)
        if self.YLabel is not None:
            plt.ylabel(self.YLabel)
        if self.Legend is not None:
            plt.legend(self.Legend, loc=self.LegendPos)

        if params.OutputDirectory is not None:
            self.OutputDirectory = params.OutputDirectory
        if (self.OutputDirectory is not None) and (self.FileName is not None):
            fullname = os.path.join(self.OutputDirectory, self.FileName)
            pprint('Saving File: {0} dpi={1}'.format(fullname, params.dpi))
            plt.savefig(fullname, dpi=params.dpi)
        plt.show()
