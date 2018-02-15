from setuptools import setup

with open('README.rst', 'r') as f:
    long_desc = f.read()

setup(
    name='sfc_models',
    packages=['sfc_models', 'sfc_models.gl_book', 'sfc_models.examples'],  # 'sfc_models.examples.scripts'],
    version='1.0.1',
    extras_require={'Charts': 'matplotlib >= 2.0'},
    package_data={'sfc_models.examples': ['scripts/*.py', 'scripts/script_list.txt']},
    description='Stock-Flow Consistent (SFC) model generation',
    long_description=long_desc,
    author='Brian Romanchuk',
    author_email='brianr747@gmail.com',
    test_suite = 'test',
    keywords=['economics', 'SFC models', 'stock-flow consistent models'],
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: Apache Software License',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.0',
                 'Programming Language :: Python :: 3.1',
                 'Programming Language :: Python :: 3.2',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Topic :: Other/Nonlisted Topic'
                 ],
    url='https://github.com/brianr747/SFC_models'
)
