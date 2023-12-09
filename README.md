# maskfill

Fill in masked values in an image

Method description is in van Dokkum (2023) (PASP)

Examples in
 example_synthetic/
 example_m51/

## Installation 

The `maskfill` code can be installed from `PyPI` via 
```
pip install maskfill
```
or the latest version from github can be retrieved via 

```
git clone https://github.com/dokkum/maskfill.git
cd maskfill 
pip intall . # or pip install -e .
```
Its dependencies are `numpy` and `astropy` (for fits handling), and Python>=3.6 for type annotations. You can create a minimal working environment for this code via 
```
mamba create -n maskfill python=3.10 numpy astropy # or conda
```

## Usage 
