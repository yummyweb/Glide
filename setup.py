from setuptools import setup

setup(
    name="glide",
    version='0.1',
    py_modules=['src.cli'],
    install_requires=[
        'Click',
        'tabulate'
    ],
    entry_points='''
        [console_scripts]
        glide=src.cli:cli
    ''',
)