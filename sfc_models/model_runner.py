# coding=utf-8
"""
Module to run models that are defined in files that meet a particular standard. To be used by
graphical user interfaces as well as the econ_platform module.

Code is under development, and may not be covered by unit tests for some time, as it is being used by
*econ_platform*, and so the unit tests would need to know about both modules.

Similarly, documentation will not appear until the econ_platform side of this has stabilised.

Since econ_platform is version 3.7+, no real validation of running on different versions. It should work,
but no guarantees...

Copyright 2019 Brian Romanchuk

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


# -----------------------------------------------------------------------------------------------
# This is code to load a module in a version agnostic fashion.
# Based on http://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
import sys
import os


if sys.version_info[0] >= 3 and sys.version_info[1] >=5:
    import importlib.util

    def loader(module_name, fpath):
        spec = importlib.util.spec_from_file_location(module_name, fpath)
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        return foo
elif sys.version_info[0] >=3 and sys.version_info[1] >=3:
    from importlib.machinery import SourceFileLoader

    def loader(module_name, fpath):
        foo = SourceFileLoader(module_name, fpath).load_module()
        return foo
else:
    import imp

    def loader(module_name, fpath):
        foo = imp.load_source(module_name, fpath)
        return foo

loader.__doc__ = """Function to load a module based on the file path.

Should work on Python 2.7+.
"""
# ----------------------------------------------------------------------------------

class ModelRunner(object):
    """
    Class to run sfc_model objects from python files (specified by a file path, so not necessarily
    on the PYTHONPATH).

    The module should have a function *build_model(string_arg)* that takes 1 or more arguments and returns a
    sfc_models.Model object. Its main function should not be called, as that will be done by this class.

    (This eventually allows stepping through the model solution.)
    """
    def __init__(self):
        self.Directory = None
        self.Model = None

    def RunModel(self, model_name, string_arg='', max_time=100, trace_step=None, solve_equilibrium=False):
        """

        :param string_arg: str
        :param model_name: str
        :param max_time: int
        :param trace_step: int
        :param solve_equilibrium: bool
        :return:
        """
        # Must be lower case
        model_name = model_name.lower()
        if self.Directory is None:
            raise ValueError('Must set Directory of ModelRunner')
        full_path = os.path.join(self.Directory, model_name + '.py')
        if not os.path.exists(full_path):
            raise ValueError('File does not exist: ' + full_path)
        mod = loader(model_name, full_path)
        try:
            self.Model = mod.build_model(string_arg)
        except NameError:
            raise ValueError('Module {0} must have build_model(string_arg) function'.format(model_name))
        self.Model.main()



