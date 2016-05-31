# coding: utf-8
from setuptools import setup, find_packages


with open('requirements.txt') as f:
    install_requires = f.read().splitlines()


setup(
    name='stock',
    version='0.4',
    author='Hiroyuki Ishii',
    url="http://f1nance.herokuapp.com/",
    py_modules=['stock'],
    packages=find_packages(),
    description='A command line tool for stock markets',
    keywords=['stock'],
    install_requires=install_requires,
    entry_points='''
        [console_scripts]
        stock=stock.cmd:cli
    ''',
)
