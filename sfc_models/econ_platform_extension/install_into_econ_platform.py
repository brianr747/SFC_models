"""
This module installs the sfc_models Provider into econ_platform.

Not particularly elegant method now, but an elegant solution is a low priority.

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
import shutil

try:
    import econ_platform
except:
    raise ImportError('Must have econ_platform package on the Python path') from None

import econ_platform.extensions


def main():
    """
    Install the provider by copying the hook file into the econ_platform_extensions directory
    :return:
    """
    targ_dir = os.path.dirname(econ_platform.extensions.__file__)
    this_dir = os.path.dirname(__file__)
    targ_file = os.path.join(targ_dir, 'hook_sfc_models.py')
    if os.path.exists(targ_file):
        print('Hook file {0}\nalready exists. This function will not overwrite it.'.format(targ_file))
        return
    print('Copying hook file from {0}\nto {1}'.format(this_dir, targ_dir))
    shutil.copyfile(os.path.join(this_dir, 'hook_sfc_models.py'),
                    targ_file)
    print('Please note that you should set configuration settings for sfc_models in econ_platform\n\n')
    print('[sfc_models]')
    print('directory={path to where you keep model files}')
    print('[ProviderList]')
    print('sfc_models={provider code, if you do not want to use SFC}')
    input('Hit <return> to finish.')




if __name__ == '__main__':
    main()