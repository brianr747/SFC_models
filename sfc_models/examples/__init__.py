"""
sfc_models.examples package
===========================

Example code is deployed here.; currently only in the form of scripts in the "scripts" sub-package. Eventually,
will develop a deployment function to push the examples to a directory specified by the user.

The Quick2DPlot() function uses matlibplot, which is the only non-base library used. If matlibplot is
not installed, the plotting fails and gives the user a warning. The user can replace matlibplot with
another plotting package fairly easily, by replacing Quick2DPlot code with replacement code.


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

import os

import sfc_models.examples.install_example_scripts


def get_file_base(fullfile):
    fname = os.path.basename(fullfile)
    pos = fname.find('.')
    if pos == -1:
        return fname
    else:
        return fname[0:pos]


def install_scripts(target_dir=None):  # pragma: no cover
    """
    Install all the example Python files into a target directory (and create an "output" subdirectory).

    If a file already exists, the script will fail. You need to copy existing files out of the way.

    :param target_dir: str
    :return:
    """
    if target_dir is None:
        if __name__ == '__main__':
            print("""
    This function installs the sfc_model example scripts into a specified target directory.
    The function will not overwrite existing files, so you will need to clean out the directory
    (saving any of your own changes) before calling this function.

    Example usage:

      sfc_models.examples.install_script('c:\\my_working_directory\\sfc_examples')

     This will install to c:\my_working_directory\sfc_examples

""")
            return
        sfc_models.examples.install_example_scripts.install(target_dir)
