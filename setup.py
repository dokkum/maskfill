from setuptools import setup, find_packages

setup(
    name='maskfill',  
    version='1.1.1',  
    author='Pieter van Dokkum & Imad Pasha',  
    author_email='pieter.vandokkum@yale.edu',  
    description='A Python package for image mask filling', 
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/dokkum/maskfill',  
    download_url = 'https://github.com/dokkum/maskfill/archive/refs/tags/v1.1.1.tar.gz',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'astropy',  
        'scipy'
    ],
    entry_points={
        'console_scripts': [
            'maskfill=maskfill.maskfill:cli',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
