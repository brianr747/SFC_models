Road To Version 1.0
===================

Introduction
------------

This document outlines what is expected to be implemented for Version 1.0 of
*sfc_models*. This version is what will be described in the to-be-published
*Introduction to SFC Models Using Python* (by Brian Romanchuk). It seems likely
that the *sfc_models* will evolve considerably as it used by others, but this
Version 1.0 will act as a base implementation that matches the book documentation.

As will be seen, very few features will be added.

There will be a "book" branch created for the source code. In this book branch,
functionality will be frozen to match what is within the book. User code developed
against the code in this branch will see a frozen *sfc_models* API. The only
developments that might occur may be an improvement of documentation and examples.
This code may be released as versions 1.0.x; e.g., 1.0.3 is the third update
on the book branch.

Economic Functionality
----------------------

No more economic functionality will be added ahead of Version 1.0.

Examples
--------

Examples will be looked at, and set to match what will appear in *Introduction to SFC Models Using Python*.

Code Cleanup
------------

Some code cleanup may be done ahead of the Version 1.0 release, but this is expected to be minor.

- Sanity checks of model output. (Do balance sheets balance?) **[Deferred]**
- Logging will be back-filled throughout the code base. The user should be able
  to see what is happening by looking at the log. **[Done]**
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