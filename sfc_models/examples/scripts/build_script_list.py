"""
build_script_list.py


This script just generates the script_list.txt file which is used for packaging.
"""

import os

excluded = ['__init__.py', 'build_script_list.py', 'run_all_scripts.py', 'build_run_all_scripts.py']


def main():
    print("Starting")
    fpath = os.path.dirname(__file__)
    print(fpath)
    flist = os.listdir(fpath)
    print(flist)
    with open(os.path.join(fpath, 'script_list.txt'), 'w') as f:
        for fname in flist:
            if fname in excluded:
                continue
            if not fname.endswith('.py'):
                continue
            print(fname)
            f.write(fname + '\n')


if __name__ == '__main__':
    main()
