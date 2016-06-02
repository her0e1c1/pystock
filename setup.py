# coding: utf-8
from setuptools import setup, find_packages
from pip.req import parse_requirements

install_requires = [str(ir.req) for ir in parse_requirements("requirements.txt", session=False)]

setup(
    name='stock',
    version='0.6',
    author='Hiroyuki Ishii',
    author_email="hiroyuki.ishii.42@gmail.com",
    url="http://f1nance.herokuapp.com/",
    py_modules=['stock'],
    packages=find_packages(),
    description='A command line tool for stock markets',
    dependency_links=[],
    keywords=['stock'],
    install_requires=install_requires,
    entry_points='''
        [console_scripts]
        stock=stock.cmd:cli
    ''',
)
