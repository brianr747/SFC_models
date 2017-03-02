TODO List
=========

**Major modelling functionality**

- Chapter 6 and 8 of Godley and Lavoie are the last major bits of economic functionality planned.
  Users will have to offer guidance on which direction to take the economics capability afterward.
- Add the idea of planned demand and supply, which can differ from realised demand and supply.
- Adaptive expectation support.
- Increased logging at the equation generation phase. May be more useful than formal
  documentation in the short run.
- Exporter and importer sectors. [Included in Chapter 8.]
- Variable naming convention.
- Standard macro aggregates automatically added in.
- More equation reduction techniques.
- Refactoring some methods to make them "private."
- Alternative solution methods, if iterative scheme does not converge.
- Graphical interface?
- Creation of an equation class, replacing the string representations?
- Subdivide financial assets (*F*) into different financial assets. [Done]
- Central banks and interest rates. [Done]
- Can we eliminate machine-generated solver safely (and efficiently)? [Done]

**Module Setup**

- Cleaner handling of examples. (Installation to local directories.) [Mainly done]
- Clean up the use of Sphinx for module documentation.
- Pypi installation clean up. [Done?]
- Source/Github installation documentation.
- Sphinx-generated HTML documentation on the web.
- Github wiki.
- Examples in Pycharm Edu.
- More detailed analysis of model configuration to aid trouble-shooting.

**Documentation**

- User high level documentation. [Book draft started by BR]
- Better documentation of class methods.
- Hide "internal" methods?
- Doctests if possible, and more documentation in unit tests.
