# Maskfill Documentation 

![GitHub Latest Release)](https://img.shields.io/github/v/release/dokkum/maskfill?logo=github)
[![PyPI version](https://badge.fury.io/py/maskfill.svg)](https://badge.fury.io/py/maskfill)
[![Documentation Status](https://readthedocs.org/projects/maskfill/badge/?version=latest)](https://maskfill.readthedocs.io/en/latest/?badge=latest)


This is the (simple!) documentation page for the `maskfill` package (van Dokkum & Pasha 2024). 

## Installation 

You can install `maskfill` from `pip` via

```
pip install maskfill
```

or, get the latest version from github via 

```
git clone https://github.com/dokkum/maskfill.git
cd maskfill 
pip install .
```
Its dependencies are only `numpy`, `scipy`, `astropy` (for `fits` handling), and `Python>=3.6` for type annotation an f-fstrings. If you wish, you can create a minimal working environment for this code via conda or mamba, e.g.,

```
mamba create -n maskfill python=3.10 numpy scipy astropy
mamba activate maskfill
```
You may also want to throw `matplotlib` in there for visualizing results within Python.

If you have a version of python < 3.6 and don't wish to create a new environment, there *is* a branch of the code on github compatible with Python pre 3.6 (back to 2.7). 

You can obtain it via: 

```
git clone --branch python<3.6 --single-branch https://github.com/dokkum/maskfill.git
cd maskfill 
pip install . # or pip install -e .
```

(assuming you have the three dependencies in a working configuration).


## Usage 

A walkthrough of all the arguments and usage in Python can be found in the Usage page. But at simplest, from your shell, in a folder containing an image and mask file: 

```
maskfill im1.fits mask.fits outname.fits
```

will run `maskfill` and save the results to a fits file. 

You can learn more about usage in the Python Usage and CLI usage pages. 

## Citing Maskfill 

If you find `maskfill` useful in your research or image handlings, please cite the code: 

```
@ARTICLE{vanDokkum:2024,
       author = {{van Dokkum}, Pieter and {Pasha}, Imad},
        title = "{A Robust and Simple Method for Filling in Masked Data in Astronomical Images}",
      journal = {\pasp},
     keywords = {Direct imaging, Astronomical techniques, Astronomy data reduction, Astronomy data analysis, 387, 1684, 1861, 1858, Astrophysics - Instrumentation and Methods for Astrophysics, Astrophysics - Astrophysics of Galaxies},
         year = 2024,
        month = mar,
       volume = {136},
       number = {3},
          eid = {034503},
        pages = {034503},
          doi = {10.1088/1538-3873/ad2866},
archivePrefix = {arXiv},
       eprint = {2312.03064},
 primaryClass = {astro-ph.IM},
       adsurl = {https://ui.adsabs.harvard.edu/abs/2024PASP..136c4503V},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}
```

```{toctree}
:maxdepth: 2
python-usage
cli
apidocs/index
```
