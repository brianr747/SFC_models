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

Road To Version 1.0
-------------------

Another text file "RoadToVersion1.txt" describes the functionality that is aimed to be
incorporated in Version 1.0 of *sfc_models*.

At the time of writing (2017-03-05), it is expected that version 0.4 will be ready. This version
involves a major refactoring of the code, and has changed behaviour.

- The framework now injects a double underscore ('__') instead of a single one ('_') between
  the sector FullCode and the local variable name. For example, the household financial assets
  are now 'HH__F' instead of 'HH_F'. Furthermore, the creation of local variables with '__' is
  blocked. This means that the presence of '__' in a variable name means that it is the full name
  of a variable; otherwise it is a local variable. (Or perhaps, a global variable, like 't'.)
- An Equation class was created. It has replaced the strings held in the Equations member of
  the Sector class. It allows us to add terms to equations, so that the financial assets and
  income equations (see below) are always well-defined. This Equation class should be used by
  the solver, but it is not yet incorporated; there is no guarantee that such a change will be
  done before version 1.0 release.
- A pre-tax income variable ('INC') was created. It is normally equal to cash inflows minus
  outflows, but there are some exceptions. (Household consumption, business dividends, etc.)
  The sectors in the framework do their best to classify cash flows as whether they affect income,
  but users may need to create exceptions (or additions) manually. (Previously, the income was
  ad hoc.)
- A new module - *sfc_models.sector* was created; it pulled the Sector class out of the models
  module. (The existing *sectors.py* may be renamed due to the name similarity.) My old
  example code that did "import *" from *sfc_models.models* no longer works. (?)

There are no *major* refactorings now expected to take place before version 1.0 release. As a result,
the project status will be changed to 'beta' in Version 0.4. Methods that are not expected to be
used by people who are not creating new classes will have '_' added in front of their name (so they
disappear from help()), but this is viewed as acceptable. Otherwise, variables and methods will
only be renamed if they are obviously not following a standard pattern.

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
- *matplotlib*: for plots in *examples*. (Essentially optional, may be required later
  if the solver algorithm needs beefing up.)

Documentation will be placed in the "docs" directory.

Examples are in the *examples* sub-package. Currently, in the form of scripts in *examples.scripts*; will develop a
deployment function later.

The test coverage on the "master" branch is 100%, and the objective is to hold that standard. There are some
sections that are effectively untestable, and there appears to be issues with some lines that are undoubtedly hit
as being marked as unreached; they have been eliminated with::
#  pragma: no cover

Change Log
----------

- **Development** Multi-file Logger, initial (constant) equilibrium calculation, markets
  with multiple supply sources, custom functions. Equation objects; used for cash flow and income.
  **Changed variable naming convention.**
- **0.3.0** Rebuilt the solver, heavy refactoring, example installation, Godley & Lavoie example framework.
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