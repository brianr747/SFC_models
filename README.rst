SFC Models Package Introduction
===============================

Introduction
------------

Creation and solution of stock-flow consistent (SFC) models. Currently under construction.

This framework generates equations algorithmically based on the connections between Sector and
Model objects. These equations are then solved using an iterative solution. The objective is that
complex models with dozens of equations can be generated with a few lines of high level code. The
user can then see how the equations arise from the sector behaviour.

For another take on SFC models in Python see: https://github.com/kennt/monetary-economics

Developed under Python 3.4, and is compatible with Python 2.7.

There are some installation instructions found in "InstallationNotes.rst"

Status Version 1.0.0
--------------------

This version of *sfc_models* is the one that is associated with the upcoming guide (estimated
release date is October 2017). The framework is hardly complete, but it is possible to use
it to create some relatively complex models. Further extensions will probably have to be
aimed at extending towards research topics of interest. The existing set of examples (and
the guide) should offer a solid starting point for other researchers.

There have been very few changes from version 0.5.0. Code cleanup may show up in minor
versions 1.0.x.

Status: Version 0.5.0
---------------------

(Section added on 2017-08-03.)

No major new functionality is expected to be added before Version 1.0. The only planned changes are beefing up
example code, and any fixes that need to be put into place.

An introductory text is nearing completion. This document is aimed to be the user documentation; the code documentation
embedded in the code base is just reference and implementation details.

Version 0.5.0 Description Syntax Change
---------------------------------------

In Version 0.5, the constructor order for Country and Sector objects has been changed.
The long_name (or description) variable was demoted to optional. It will now
be possible to create objects with just two arguments::

ca = Country(model_object, 'CA')

instead of (old syntax)::

ca = Country(model_object, 'Canada', 'CA')

In my view, this is a major quality of life improvement for future users, at the cost of breaking
what I assume is still a small base of external user's code.

Road To Version 1.0
-------------------

Another text file "RoadToVersion1.rst" describes the functionality that is aimed to be
incorporated in Version 1.0 of *sfc_models*.

Version 0.4.0 is being released on 2017-03-06. This version
involves a major refactoring of the code, and has changed behaviour.

- The framework now injects a double underscore ('__') instead of a single one ('_') between
  the sector FullCode and the local variable name. For example, the household financial assets
  are now 'HH__F' instead of 'HH_F'. Furthermore, the creation of local variables with '__' is
  blocked. This means that the presence of '__' in a variable name means that it is the full name
  of a variable; otherwise it is a local variable. (Or perhaps a global variable like 't'.)
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
  module. The existing *sectors.py* was renamed to *sector_definitions.py*. My old
  example code that did "import \*" from *sfc_models.models* no longer works. (?)

There are no *major* refactorings now expected to take place before version 1.0 release.
**(Update: the previous statement turned out to be dead wrong; see the discussion of
the description change above.)** As a result, the project status will be changed to
'beta' in Version 0.4. Methods that are not expected to be used by people who are not
creating new classes will have '_' added in front of their name (so they disappear from
help()), but this is viewed as acceptable. Otherwise, variables and methods will only be
renamed if they are obviously not following a standard pattern.

Sub-package: gl_book
--------------------

The sub-package sfc_models.gl_book contains code to generate models from the text "Monetary Economics"
by Wynne Godley and Marc Lavoie. The test process uses target output calculated elsewhere to
validate that *sfc_models* generates effectively the same outcome. It should be noted that
*sfc_models* has to approach equation-building differently than humans, and so there are more
equations (and are labelled very differently). One needs to map the variables in "Monetary Economics"
to those generated by *sfc_models* to validate that they get the same output.

The previously mentioned GitHub package by "kennt" consists of well-documented solutions of those models in IPython
notebooks.

Models implemented (objects here generally use the same name name as Monetary Economics):

- **Chapter 3** Model SIM, SIMEX
- **Chapter 4** Model PC
- **Chapter 6** Model REG (two versions here; REG and REG2). (I have a variant of model OPENG as well.)

Solution Method
---------------

The single-period solution of a SFC model relies on market-clearing (not necessarily relying on price adjustments,
unlike mainstream models). Market clearing relies on solving many simultaneous equations.

At present, the machine-generated code uses an iterative approach to solve *x = f(x)* (where *x* is a vector).
We just passing an initial guess vector through *f(x)* and hope it converges.

This works for the simple models tested so far. The objective is to augment this by a brute-force search technique that
relies upon economic intuition to reduce the dimension of the search space. This will be needed for flexible
currency models.

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

- **1.0.0** Locking down the version associated with the guide.
- **0.5.0** Change to sector constructor order, examples development.
- **0.4.3** install_examples() GUI added. Python 2.7 fixes.
- **0.4.2** Small changes, import from *sfc_models.objects* supported.
- **0.4.1** Fixed packaging problem from Version 0.4.0.
- **0.4.0** *Packaged incorrectly* Multi-file Logger, initial (constant) equilibrium calculation, markets
  with multiple supply sources, custom functions. Equation objects used in model creation.
  **Changed variable naming convention, eliminated the Sector.Equations member.** Considerable
  refactoring, methods for developer use have been hidden with leading underscore. Example code
  cleanup.
- **0.3.0** Rebuilt the solver, heavy refactoring, example installation, Godley & Lavoie example framework.
- **0.2.1** Cleaned up examples layout.
- **Version 0.2**  (Should have been 0.2.0 - oops)
  First deployment of package to PyPi. Base functionality operational, little documentation.
- Earlier versions: Only available as source on Github.


License/Disclaimer
------------------

Copyright 2016-2017 Brian Romanchuk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.