SFC Models Package Introduction
===============================

Introduction
------------

Creation and solution of stock-flow consistent (SFC) models. Currently under construction.

At present, the module *sfc_models.iterative_machie_generator.py* imports a text block of
equations, and then writes a python module that implements that system of equations.

Although such functionality is nice, the objective is to build modules that generate the systems of
equations. That is, the user will specify the high-level sector description of the economy (which may include
multiple countries), and the high-level description will be parsed to generate the low-level equations.

For another take on SFC models in Python see: https://github.com/kennt/monetary-economics

Developed under Python 3.4, and is compatible with Python 2.7.

Sub-package: gl_book
--------------------

The subpackage sfc_models.gl_book contains code to generate models from the text "Monetary Economics"
by Wynne Godley and Marc Lavoie. Since the ultimate objective is to generate the equations algorithmically,
these models are only used for comparative purposes.

The previously mentioned GitHub package by "kennt" consists of well-documented solutions of those models in IPython
notebooks.

Solution Method
---------------

The single-period solution of a SFC model relies on market-clearing (not necessarily relying on price adjustments,
unlike mainstream models). Market clearing relies on solving many simultaneous equations.

At present, the machine-generated code uses an iterative approach to solve *x = f(x)* (where *x* is a vector).
We just passing an initial guess vector through *f(x)* and hope it converges.

This works for the simple models tested so far. The objective is to augment this by a brute-force search technique that
relies upon economic intuition to reduce the dimension of the search space.

Dependencies
------------
- *matplotlib*: for plots in *examples*. (May be required later.)

Documentation will be placed in the "docs" directory.

Examples are in the *examples* sub-package. Currently, in the form of scripts in *examples.scripts*; will develop a
deployment function later.

The test coverage on the "master" branch is 100%, and the objective is to hold that standard. There are some
sections that are effectively untestable, and there appears to be issues with some lines that are undoubtedly hit
as being marked as unreached; they have been eliminated with::
#  pragma: no cover

Change Log
----------

- **0.2.1** Cleaned up examples layout.
- **Version 0.2**  (Should have been 0.2.0 - oops)
  First deployment of package to PyPi. Base functionality operational, little documentation.
- Earlier versions: Only available as source on Github.


License/Disclaimer
------------------

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