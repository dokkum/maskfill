import numpy as np
import argparse
from astropy.io import fits
from typing import Union

__version__ = "1.0"

def nan_filter(image, size, orgimage, operator):
    """
    Apply mean or median filter to replace NaN values in an image
    Cannot be done with median or generic filters in scipy.ndimage
    Args:
        image (np.ndarray): Input image
        size (int): Size of the filter
        orgimage (np.ndarray): Original image, for checking if the pixel was originally masked
        operator (str): Filter operation ('mean' or 'median')

    Returns:
        np.ndarray: Filtered image
    """
    filtered_image = np.copy(image)

    h = size // 2

    # Pad the image with NaNs to handle pixels on the edges correctly
    padded_image = np.pad(image, ((h, h), (h, h)), mode='constant', constant_values=np.nan)

    for i in range(h, padded_image.shape[0] - h):
        for j in range(h, padded_image.shape[1] - h):
            window = padded_image[i - h:i + h + 1, j - h:j + h + 1]
            valid_values = window[~np.isnan(window)]
            # Only replace masked pixel if it is the first time, or if it was never masked
            if len(valid_values) > 0 and (np.isnan(image[i - h, j - h]) or not np.isnan(orgimage[i - h, j - h])):
                filtered_image[i - h, j - h] = np.nanmean(valid_values) if operator == "mean" else np.nanmedian(valid_values)

    return filtered_image

def maskfill(input : Union[np.ndarray,str],
            mask : Union[np.ndarray,str],
            ext: int = 0,
            size: int = 3,
            operator: str = 'median',
            smooth: bool = True,
            writesteps: bool=False,
            output: str = None,
            verbose: bool = False,
            ):
    """Maskfill function; used to smoothly iteratively fill masks in images. 
    See van Dokkum et al. 2023 (PASP) for details.

    Parameters
    ----------
    input : Union[np.ndarray,str]
        input image, either a filepath to fits file or the ndarray directly.
    mask : Union[np.ndarray,str]
        mask image, either a filepath to fits file or the ndarray directly. (0=good, 1=bad)
    ext : int, optional
        fits extension if input/masks are fname, by default 0
    size : int, optional
        size of median filter, by default 3
    operator : str, optional
        either 'mean' or 'median', by default 'median'
    smooth : bool, optional
        whether to boxcar smooth the final image, by default True
    writesteps : bool, optional
        write intermediate fits files to disk with iterations of filling, by default False
    output : str, optional
        save output to this filepath (in addition to returning filled array), by default None
    verbose : bool, optional
        verbose printouts, by default False

    Returns
    -------
    _type_
        _description_
    """
    if isinstance(input,str):
        im = fits.getdata(input,ext)
    else:
        im = input 
    if isinstance(mask,str):
        mask = fits.getdata(mask,ext)
    else:
        mask = mask
    im_masked_initial = np.where(mask, np.nan, im)
    # Iterate until all masked pixels are replaced
    counter = 1
    im_masked = np.copy(im_masked_initial)
    while np.isnan(im_masked).any():
        if verbose:
            print("Replacing masked pixels, iteration {}".format(counter))
        # Apply mean or median filter based on the specified operator
        im_masked = nan_filter(im_masked, size, im_masked_initial, operator)
        # Write intermediate steps, if desired
        if writesteps:
            im_filled_iter = im_masked * mask + (1 - mask) * im
            fits.writeto("_iter_{}.fits".format(counter), im_filled_iter, overwrite=True)
        counter += 1

    # Fill in masked pixels in the input image using the filtered masked image
    im_filled = im_masked * mask + (1 - mask) * im
    if smooth:
        if verbose:
            print("Doing final boxcar smoothing")
        im_masked = nan_filter(im_filled, size, im_filled, "mean")
        im_filled = im_masked * mask + (1 - mask) * im
    else:
        if verbose:
            print('Boxcar smoothing not requested.')
    if verbose:
        print("\nDone!\n")
    if output is not None:
        # Write filled image to output fits file
        fits.writeto(output, im_filled, overwrite=True)
    else:
        print('No output set; filled image being returned.')
    return im_filled 


def cli():
    parser = argparse.ArgumentParser()

    # Define command line arguments
    parser.add_argument("input", help="input image", type=str)
    parser.add_argument("mask", help="mask image, with values 0 = good, 1 = bad", type=str)
    parser.add_argument("output", help="output image", type=str)
    parser.add_argument("-v", "--verbose", help="print actions", action="store_true")
    parser.add_argument("-s", "--size", help="scale of median filter (default = 3)", type=int)
    parser.add_argument("-o", "--operator", help="replace pixels with mean or median (default = median)", type=str)
    parser.add_argument("-n", "--nosmooth", help="omit boxcar smoothing at the end (default = False)", action="store_true")
    parser.add_argument("-w", "--writesteps", help="write result after each iteration, as _iter_#.fits", action="store_true")
    args = parser.parse_args()

    # Read input image and mask image (both fits)
    im = fits.getdata(args.input)
    mask = fits.getdata(args.mask)
    im_masked_initial = np.where(mask, np.nan, im)

    # Set the size of the filter (larger sizes are faster but less accurate)
    size = args.size if args.size and args.size > 2 else 3

    # Set boxcar smoothing at the end to True, unless --nosmooth flag is set
    boxcar = not args.nosmooth

    # Set the operator for replacing pixels (mean is faster but less accurate)
    operator = args.operator if args.operator and (args.operator == "mean" or args.operator == "median") else "median"

    if args.verbose:
        print("\nFilling in masked regions in image {}".format(args.input))
        print("  Size of filter = {}".format(size))
        print("  Operation for replacing pixels = {}\n".format(operator))

    # Iterate until all masked pixels are replaced
    counter = 1
    im_masked = np.copy(im_masked_initial)
    while np.isnan(im_masked).any():
        if args.verbose:
            print("Replacing masked pixels, iteration {}".format(counter))
        # Apply mean or median filter based on the specified operator
        im_masked = nan_filter(im_masked, size, im_masked_initial, operator)
        # Write intermediate steps, if desired
        if args.writesteps:
            im_filled_iter = im_masked * mask + (1 - mask) * im
            fits.writeto("_iter_{}.fits".format(counter), im_filled_iter, overwrite=True)
        counter += 1

    # Fill in masked pixels in the input image using the filtered masked image
    im_filled = im_masked * mask + (1 - mask) * im

    # Boxcar-smooth filled areas to reduce artificial sharp features, if desired
    if boxcar:
        if args.verbose:
            print("Doing final boxcar smoothing")
        im_masked = nan_filter(im_filled, size, im_filled, "mean")
        im_filled = im_masked * mask + (1 - mask) * im

    if args.verbose:
        print("\nDone!\n")

    # Write filled image to output fits file
    fits.writeto(args.output, im_filled, overwrite=True)


if __name__ == "__main__":
    cli()

