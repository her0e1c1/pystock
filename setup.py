from setuptools import setup, find_packages


with open('requirements.txt') as f:
    install_requires = f.read().splitlines()


setup(
    name='stock',
    version='0.1',
    author='Hiroyuki Ishii',
    py_modules=['stock'],
    packages=find_packages(),
    description='A command line tool for stock markets',
    keywords=['stock'],
    install_requires=install_requires,
    entry_points='''
        [console_scripts]
        pystock=stock.cmd:cli
    ''',
)
