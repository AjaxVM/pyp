
import os
from setuptools import find_packages, setup

setup(
    name='pyp_manager',
    version='0.0.1',
    description='WIP project management tool for Python',
    long_description='TODO',
    license='MIT',
    classifiers=[], # todo,
    url='https://github.com/AjaxVM/pyp-manager',
    keywords='todo',
    author='Matthew Roe',
    author_email='roebros@gmail.com',
    install_requires=[
        'jsonschema'
    ],
    package_dir={'': 'src'},
    packages=find_packages(
        where='src',
        exclude=[] #todo
    ),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'pyp=pyp_manager.main:run'
        ]
    }
)
