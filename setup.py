import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='dashdash',
    version='0.0.0',
    author='Robert Gale',
    author_email='rcgale@gmail.com',
    packages=setuptools.find_packages(),
    url='https://github.com/rcgale/dashdash',
    description='Easiily turn a function into a command line app',
    install_requires=[
        "docstring-parser>=0.7.3"
    ]
)

