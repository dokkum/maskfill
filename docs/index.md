# Maskfill Documentation 

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

```{toctree}
:maxdepth: 2
python-usage
cli
apidocs/index
```
