from setuptools import setup, find_packages


setup(
    name='pystock',
    version='0.1',
    py_modules=['pystock'],
    packages=find_packages(),
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        pystock=pystock.lib:cli
    ''',
    )
