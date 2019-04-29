
from setuptools import find_packages, setup

setup(
    name='pyp',
    version='0.0.1',
    description='WIP project management tool for Python',
    long_description='TODO',
    license='MIT',
    classifiers=[], # todo,
    url='https://github.com/AjaxVM/pyp',
    keywords='todo',
    author='Matthew Roe',
    author_email='roebros@gmail.com',
    package_dir={'': 'src'},
    packages=find_packages(
        where='src',
        exclude=[] #todo
    ),
    entry_points={
        'console_scripts': [
            'pyp=pyp.main:run'
        ]
    }
)
