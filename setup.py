from distutils.core import setup
from setuptools import find_packages


setup(
    name='django_smartdbstorage',
    version='0.1.1',
    author='Dominique PERETTI',
    author_email='dperetti@lachoseinteractive.net',
    packages=find_packages(),
    #scripts=['bin/xx.py'],
    url='http://dperetti.github.com/Django-SmartDBStorage',
    license='LICENSE.txt',
    description='A Django Model based file storage.',
    long_description=open('README.txt').read(),
    install_requires=[
        'South>=0.7.3'
    ],
)
