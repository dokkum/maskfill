from setuptools import setup, find_packages

setup(
    name='maskfill',  # Package name
    version='1.0',  # Initial version
    author='Pieter van Dokkum',  # Replace with your name
    author_email='pieter.vandokkum@yale.edu',  # Replace with your email
    description='A Python package for image mask filling',  # Replace with your description
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/dokkum/maskfill',  # Replace with the URL to your repo
    download_url = 'https://github.com/dokkum/maskfill/archive/refs/tags/v1.0.tar.gz',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'astropy',  # Add other dependencies as needed
    ],
    entry_points={
        'console_scripts': [
            'maskfill=maskfill.maskfill:cli',
        ],
    },
    classifiers=[
        # Intended audience, project status, license, supported Python versions, etc.
        # Example:
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
