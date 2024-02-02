### CLI Usage 

When you install `maskfill` it will create a `maskfill` executable callable from the shell. You can print the usage via 
```
maskfill -h
```
which will return something like this: 

```bash
usage: maskfill [-h] [-e EXTENSION] [-v] [-s SIZE] [-o OPERATOR] [-n] [-w] input mask output

positional arguments:
  input                 input image
  mask                  mask image, with values 0 = good, 1 = bad
  output                output image

options:
  -h, --help            show this help message and exit
  -e EXTENSION, --extension EXTENSION
                        fits extension of data
  -v, --verbose         print actions
  -s SIZE, --size SIZE  scale of median filter (default = 3)
  -o OPERATOR, --operator OPERATOR
                        replace pixels with mean or median (default = median)
  -n, --nosmooth        omit boxcar smoothing at the end (default = False)
  -w, --writesteps      write result after each iteration, as _iter_#.fits
```

The simplest call is something like 
```
maskfill im.fits mask.fits out.fits
```

or
```
maskfill im mask out #file extension assumed to be .fits
```

in which you provide the input image, mask image, and name of the output file (if the `.fits` is omitted, `maskfill` will add it, though if your files have alternate extensions like `.fit` you should specify the full name). There are also several optional arguments and flags. 

- `-e X` or `--extension X`: if the image and mask are not in the 0th fits extension, specify it here 
- `-s X` or `--size X`: if you want a larger window kernel than the minimum 3x3, specify it here (faster, but less accurate results)
- `-o median` or `--operator median`: either 'median' or 'mean', defines how masked pixels are filled in based on their neighbors
- `-n` or `--nosmooth`: disable a final-step boxcar smoothing of the filled in mask pixels
- `-w` or `--writesteps`: write `_iter_N` fits files after each iteration of the algorithm (default is False)
- `-v` or `--verbose`: verbose output (shows the progress of iterations and number of remaining masked pixels).

The output is saved in the fits file with the provided output name. By default, after infilling, a smoothing step (using the same window, but a `mean` filter) is used to reduce sharp edges introduced by the iterative infilling. When enabled, the output fits file will contain the smoothed output image in the 0th extension, and the unsmoothed version post infilling in the 1st extension. If `nosmooth` is flagged, the 0th extension will contain the unsmoothed output. Information about which type of output is in which extension is added to the header. 