"""
plot_for_examples.py

Plotting class to generate 2-D charts for examples. This file is the only one (other than another example)
that depends upon matplotlib. If matplotlib is not imported (that is, not installed), does
a fall back operation (dump to console, and eventually, a csv). The user can either find a plotting
function that works, or import the csv data.

I have isolated this so that it is possible to run examples with no external dependencies.

To install matplotlib, running "pip install matplotlib" in the approppriate Python "Scripts" directory
should do the job. Unfortunately, it can sometimes fail. There is up-to-date documentation on the internet;
I do not want to attempt to cover the details here.

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

try:
    import matplotlib.pyplot as plt
except ImportError:
    print("Unable to load matplotlib; no graphing output is possible!")
    plt = None


class Quick2DPlot(object):
    def __init__(self, x, y, title='', run_now=True):
        self.X = x
        self.Y = y
        self.Title = title
        self.XLabel = None
        self.YLabel = None
        self.Legend = None
        if run_now:
            self.DoPlot()

    def DoPlot(self):
        if plt is None:
            print('Attempted to plot the following data; cannot to do because cannot import matplotlib')
            print('%s %20s' % ('X', 'Y'))
            for i in range(0, len(self.X)):
                print('%f %20f', (self.X[i], self.Y[i]))
            return
        if type(self.X[0]) == list:
            plt.plot(self.X[0], self.Y[0], self.X[1], self.Y[1], marker='o')
        else:
            plt.plot(self.X, self.Y, marker='o')
        if len(self.Title) > 0:
            plt.title(self.Title)
        plt.grid()
        if self.XLabel is not None:
            plt.xlabel(self.XLabel)
        if self.YLabel is not None:
            plt.ylabel(self.YLabel)
        if self.Legend is not None:
            plt.legend(self.Legend)
        plt.show()
