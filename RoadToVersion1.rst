Road To Version 1.0
===================

Introduction
------------

This document outlines what is expected to be implemented for Version 1.0 of
*sfc_models*. This version is what will be described in the to-be-published
*Introduction to SFC Models Using Python* (by Brian Romanchuk). It seems likely
that the *sfc_models* will evolve considerably as it used by others, but this
Version 1.0 will act as a base implementation that matches the book documentation.

There will be a "book" branch created for the source code. In this book branch,
functionality will be frozen to match what is within the book. User code developed
against the code in this branch will see a frozen *sfc_models* API. The only
developments that might occur may be an improvement of documentation and examples.
This code may be released as versions 1.0.x; e.g., 1.0.3 is the third update
on the book branch.

This document outlines the economic functionality that will be added, and
then the code functionality. The list of features to be added is viewed as frozen;
ideas that may be useful for the future will be added to the TODO document, but
development will occur in versions 1.1 and later.

Economic Functionality
----------------------

The following models from *Monetary Economics* (Godley and Lavoie) are hoped to
be implemented.

- *Model REG* from Chapter 6. **[DONE]**
- *Model REG2* = *Model REG* with sectors in two Country objects. **[DONE]**
- *Model OPEN* from Chapter 6. *[Started]*
- *Model DIS* from Chapter 9.
- Possibly: *Model DISINF* from Chapter 9.
- Possibly: *Model INSOUT* from Chapter 10.

Furthermore, a SFC model from the literature may be implemented.

The implementation of these models will require more work on international models
(*Model OPEN*) and prices and inventories (*DIS*, *DISINF*).

Code Cleanup
------------

The following are the areas of code that will be examined.

- Sanity checks of model output. (Do balance sheets balance?)
- Logging will be back-filled throughout the code base. The user should be able
  to see what is happening by looking at the log. **[Started.]**
- An Equation class may be added. Previously, equations were just lists of
  strings (str). Only limited functionality is expected to be embedded in
  Version 1.0; the main feature is ensure that the user operations are safe. **[DONE]**
- Methods that are viewed as "private" will be renamed with "_" in their
  names; they will not show up in help **[Started.]**
- Refactoring to ensure greater consistency of naming and parameter usage.
- Allow users to define functions to be used within equations. **[DONE]**
- Example scripts will either be updated or moved to the "deprecated" folder. **[DONE]**

Documentation
-------------

The main documentation work will revolve around adding doc strings to all
methods. Example scripts are expected to provide more context. Of course, there
will be a book available for sale explaining the high level working of the library.

The book will include a technical description of the solver, as well as an
explanation of the object hierarchy.

Excerpts of the book will be placed on the BondEconomics blog
(http://bondeconomics.com ), and may be incorporated within the documentation base.

Since it is expected  that the library will evolve once others start to use it,
placing too much high level documentation within the library early on may be
counter-productive. The book is aimed to work against the fixed Version 1.0 of the
code base, but the library documentation needs to be compatible with Versions
2.0, etc.