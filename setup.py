from distutils.core import setup
from setuptools import find_packages


setup(
    name='django_smartdbstorage',
    version='0.1.0',
    author='Dominique PERETTI',
    author_email='dperetti@lachoseinteractive.net',
    packages=find_packages(),
    #scripts=['bin/xx.py'],
    url='https://github.com/dperetti/Django-SmartDBStorage',
    license='LICENSE.txt',
    description='A Django Model based file storage.',
    long_description=open('README.txt').read(),
    install_requires=[
        # "Django >= 1.4",
    ],
)
