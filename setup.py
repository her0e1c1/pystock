from setuptools import setup, find_packages


setup(
    name='s',
    version='0.1',
    py_modules=['s'],
    packages=find_packages(),
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        import_company=s.commands:import_company
    ''',
    )
