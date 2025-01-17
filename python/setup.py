from setuptools import setup, find_packages

setup(
    name='list-sync',
    version='0.1',
    packages=find_packages(),
    install_requires=[],
    author='Babini Stefano',
    author_email='stefano.babini5@studio.unibo.it',
    description='A simple library to syncronize rows with a kafka topic',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ste-script/list-sync',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
