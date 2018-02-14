# coding=utf-8
Installation Notes
==================

These installation notes are very preliminary.

Simplest: pip
-------------

The sfc_models package is available at the Python Package Repository (pypi.org). The *pip*
installation script will do the work for you

pip install sfc_models

How you invoke the pip script varies by operating system. I leave finding the appropriate
instructions to the reader as a web search (particularly as I only have a Windows machine,
so I have no way to test other operating system instructions).

The next step you will probably want to do is to get the example code. There is a utility
script "install_examples" that will install the example scripts into a directory of your
choice. It will give a popup menu for choosing the save location (which worked on the
author's machine).

In a Python interpreter, you can do

from sfc_models.objects import *
install_examples

This function is found in the "examples" directory, which is outside the "sfc_models" package
directory.

Alternatively, one could go to the GitHub sfc_models repository, and download the example scripts
from the directory.

GitHub
------

If you want to work with the latest version of the code, you will need to clone the
repository from GitHub. You will also need to know Python imports code from a package.

This would be more appropriate for an advanced reader who already understands Python,
and so the presumption is that you could set this up. Since you would be working with the
entire code repository, it would be easy to access the examples.

Development Environment
-----------------------

An integrated development environment (IDE) should make it easy to install the package. The
author uses PyCharm, and installation is straightforward.