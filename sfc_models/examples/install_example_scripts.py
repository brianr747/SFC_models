"""
install_example_scripts.py

Run "install([path])" to install all of the example scripts into a directory.  If a file already exists, the
script throws an error. The user has to clean existing code out of the way, even if it is not modified.

This is somewhat clumsy, but this is a stop-gap installation measure. There is support for installation of
"data files" within the installation framework, but I want to make sure the users know where the
scripts are.


Copyright 2017 Brian Romanchuk

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
from pkg_resources import resource_string


def install(target_dir):
    """
    Install all the example Python files into a target directory (and create an "output" subdirectory).

    If a file already exists, the script will fail. You need to copy existing files out of the way.

    :param target_dir: str
    :return:
    """
    if not os.path.isdir(target_dir):
        raise ValueError('{0} is not a directory'.format(target_dir))
    print('Installing example scripts to: ' + target_dir)
    if not os.path.isdir(os.path.join(target_dir, 'output')):
        print('Creating "output" subdirectory')
        os.mkdir(os.path.join(target_dir, 'output'))
    print('Fetching script list.')
    file_list = resource_string('sfc_models.examples', 'scripts/script_list.txt')
    print('Writing files')
    for fname in file_list.split('\n'):
        fname = fname.strip()
        if len(fname) == 0:
            continue
        print(fname)
        full_name = os.path.join(target_dir, fname)
        if os.path.isfile(full_name):
            raise ValueError('File already exists; must remove before running: ' + full_name)
        contents = resource_string('sfc_models.examples', 'scripts/' + fname)
        with open(full_name, 'w') as f:
            f.write(contents)

