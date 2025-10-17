from typing import Union, Callable 
import numpy as np 
from astropy.io import fits 
import argparse 
from scipy.signal import convolve2d

import torch
import torch.nn.functional as F
from typing import Optional

def find_nan_indices(arr:np.ndarray,window_size:int=3):
    """Find all NaN indices in an array which have at least 1 non-NaN neighbor in the given window

    Parameters
    ----------
    arr : np.ndarray
        array to find NaNs with >0 non-NaN neighbors in 
    window_size : int, optional
        window size (3x3 means the eight pixels around a given pixel), by default 3

    Returns
    -------
    np.ndarray
        all indices where the condition of a NaN with >0 non-NaN neighbor is True
    """
    if window_size % 2 == 0:
        raise ValueError("Window_size must be odd")
    nan_mask = np.isnan(arr)
    # Define the convolution kernel to count non-NaN neighbors
    kernel = np.ones((window_size, window_size), dtype=int)
    kernel[window_size // 2, window_size // 2] = 0  # Ignore the center pixel
    # Count the non-NaN neighbors for each element
    non_nan_neighbors = convolve2d(~nan_mask, kernel, mode='same', boundary='fill', fillvalue=0)
    # Find indices where the element is NaN and has at least one non-NaN neighbor
    result_indices = np.argwhere(nan_mask & (non_nan_neighbors > 0))
    return result_indices



def find_nan_indices_torch(arr: torch.Tensor, window_size: int = 3) -> torch.Tensor:
    """Find all NaN indices in a tensor which have at least 1 non-NaN neighbor in the given window

    Parameters
    ----------
    arr : torch.Tensor
        tensor to find NaNs with >0 non-NaN neighbors in
    window_size : int, optional
        window size (3x3 means the eight pixels around a given pixel), by default 3

    Returns
    -------
    torch.Tensor
        all indices where the condition of a NaN with >0 non-NaN neighbor is True
        Shape: (N, 2) where N is the number of qualifying indices
    """
    if window_size % 2 == 0:
        raise ValueError("Window_size must be odd")

    device = arr.device
    dtype = arr.dtype

    # Create NaN mask
    nan_mask = torch.isnan(arr)  # True where NaN

    # Create convolution kernel to count non-NaN neighbors
    # Use the same dtype as input tensor
    kernel = torch.ones((1, 1, window_size, window_size), device=device, dtype=dtype)
    kernel[0, 0, window_size // 2, window_size // 2] = 0  # Ignore center pixel

    # Convert non-NaN mask to same dtype as input for convolution
    non_nan_mask = (~nan_mask).to(dtype)  # True (1.0) where not NaN

    # Add batch and channel dimensions for conv2d
    non_nan_mask_4d = non_nan_mask.unsqueeze(0).unsqueeze(0)  # Shape: (1, 1, H, W)

    # Count non-NaN neighbors using convolution
    # padding='same' equivalent: pad = (window_size - 1) // 2
    pad = (window_size - 1) // 2
    non_nan_neighbors = F.conv2d(non_nan_mask_4d, kernel, padding=pad)

    # Remove batch and channel dimensions
    non_nan_neighbors = non_nan_neighbors.squeeze(0).squeeze(0)  # Shape: (H, W)

    # Find indices where element is NaN AND has at least one non-NaN neighbor
    condition = nan_mask & (non_nan_neighbors > 0)

    # Get indices where condition is True
    result_indices = torch.nonzero(condition, as_tuple=False)  # Shape: (N, 2)

    return result_indices

def process_masked_pixels(input_image : np.ndarray,
                        pad_width : int, 
                        mask : np.ndarray = None, 
                        operator_func : Callable = np.nanmean):
    """Helper function to process masked pixels in the output image.
    Returns the updated output array.

    Parameters
    ----------
    input_image : np.ndarray
        image to process
    pad_width : int
        width to pad image (depends on window size)
    mask : np.ndarray, optional
        if provided, the pixels to be windowed will be chosen from the mask, else it will fill any NaN values in `input_image`, by default None
    operator_func : Callable, optional
        operation to apply to the masked or NaN pixels in the window of +/- padwidth, by default np.nanmean
        For maskfill to work, the operator function must compute statistics while ignoring NaN values in the input.

    Returns
    -------
    np.ndarray
        Image with all masked or NaN pixels that have neighboring non-NaN values replaced by the operator func applied to those neighbors.
    """
    padded_output = np.pad(input_image, pad_width, 'constant', constant_values=np.nan)
    #if mask provided, index list generated from mask. Else, index list is any NaN in input image.
    if mask is not None:
        ind_masked = np.column_stack(np.where(mask)) 
    else:
        ind_masked = find_nan_indices(input_image)
    for i in ind_masked:
        y = i[0] 
        x =i[1]
        x_padded, y_padded = x + pad_width, y + pad_width
        local_window = padded_output[y_padded-pad_width:y_padded+pad_width+1, 
                                    x_padded-pad_width:x_padded+pad_width+1]
        input_image[y, x] = operator_func(local_window)
    return input_image


def process_masked_pixels_torch(input_image: torch.Tensor,
                                    pad_width: int,
                                    mask: Optional[torch.Tensor] = None,
                                    operator_func: Callable = torch.nanmean) -> torch.Tensor:
    """Highly optimized version using im2col-style operations for maximum vectorization.

    This version is faster for large numbers of masked pixels but uses more memory.
    """
    device = input_image.device
    dtype = input_image.dtype
    H, W = input_image.shape

    # Create a copy to avoid modifying input
    output = input_image.clone()

    # Determine which pixels to process
    if mask is not None:
        pixels_to_process = mask
    else:
        # Find NaN pixels that have non-NaN neighbors
        nan_indices = find_nan_indices_torch(input_image, window_size=2 * pad_width + 1)
        if len(nan_indices) == 0:
            return output

        pixels_to_process = torch.zeros_like(input_image, dtype=torch.bool)
        pixels_to_process[nan_indices[:, 0], nan_indices[:, 1]] = True

    # Pad the image
    padded_image = F.pad(input_image, (pad_width, pad_width, pad_width, pad_width),
                         mode='constant', value=float('nan'))

    # Use unfold to extract all possible windows
    window_size = 2 * pad_width + 1
    windows = padded_image.unfold(0, window_size, 1).unfold(1, window_size, 1)
    # Shape: (H, W, window_size, window_size)
    windows = windows.reshape(H, W, -1)  # Shape: (H, W, window_size^2)

    # Select only windows for pixels we want to process
    mask_indices = torch.nonzero(pixels_to_process, as_tuple=True)
    selected_windows = windows[mask_indices]  # Shape: (N_masked, window_size^2)

    if len(selected_windows) > 0:
        # Apply operator function - handle both torch and numpy functions
        if operator_func == torch.nanmean or operator_func.__name__ == 'nanmean':
            valid_mask = ~torch.isnan(selected_windows)
            windows_sum = torch.where(valid_mask, selected_windows, torch.tensor(0.0, device=device, dtype=dtype)).sum(
                dim=1)
            valid_counts = valid_mask.sum(dim=1).to(dtype)
            valid_counts = torch.where(valid_counts > 0, valid_counts, torch.tensor(1.0, device=device, dtype=dtype))
            results = windows_sum / valid_counts
        elif operator_func == torch.nanmedian or operator_func.__name__ == 'nanmedian':
            results = torch.nanmedian(selected_windows, dim=1).values
        else:
            # For custom operators, handle numpy return values
            results_list = []
            for window in selected_windows:
                result = operator_func(window)
                # Convert numpy scalars to torch tensors
                if hasattr(result, 'item'):  # numpy scalar
                    result = torch.tensor(result.item(), device=device, dtype=dtype)
                elif not isinstance(result, torch.Tensor):
                    result = torch.tensor(float(result), device=device, dtype=dtype)
                results_list.append(result)
            results = torch.stack(results_list)

        # Update output
        output[mask_indices] = results

    return output

def maskfill(input_image : Union[str,np.ndarray], 
            mask : Union[str,np.ndarray], 
            ext : int = 0, 
            size : int = 3, 
            operator : str = 'median', 
            smooth : bool = True, 
            writesteps : bool = False, 
            output_file : str = None, 
            verbose : bool = False,
            torch : bool = False
             ):
    """Maskfill function used to smoothly iteratively fill masks in images. 
    See van Dokkum et al. 2023 (PASP) for details.

    Parameters
    ----------
    input_image : Union[str,np.ndarray]
        input image; either a path to a `.fits` file or a numpy ndarray
    mask : Union[str,np.ndarray]
        mask image; either a path to a `.fits` file or a numpy ndarray [0 = good, 1 = bad/fill location]
        Note that any NaN values in the mask file will be ignored (i.e., treated as 0). 
    ext : int, optional
        fits extension in input and mask where data are stored, by default 0
    size : int, optional
        size for the filter to use (must be odd) --- a size of three implies the 8 pixels surrounding 1 pixel are considered, by default 3
    operator : str, optional
        fill operator either 'median' or 'mean', by default 'median'
    smooth : bool, optional
        whether to boxcar smooth the filled pixels using a mean with kernel = `size` after filling, by default True
    writesteps : bool, optional
        if True, save the output image of each iteration of the filling process, by default False
    output_file : str, optional
        Write the final image to a fits file (if smoothing is enabled, a second extension with the non-smoothed version will be added), by default None
    verbose : bool, optional
        Flag for verbose messages during the filling, by default False
    torch : bool, optional
        Flag for torch, by default False

    Returns
    -------
    output1, output2: np.ndarray, np.ndarray
        output (filled) image. If no smoothing is requested, the output will be `output,None`
        If smoothing is requested, the output will be `smoothed_output, output` (i.e., both the smoothed and unsmoothed output).
        One can ignore the second output by calling `smoothed_output, _ = maskfill(...)`
        Similarly, if an output filename is provided, the 0th extension will have the output image smoothed if smoothing was
        requested, or unsmoothed if not. If smoothing was requested, the unsmoothed version will be stored in the 1st extension.
    """
    if torch:
        # Check that torch is installed
        try:
            import torch
        except ImportError:
            print('Pytorch is not installed. Please either install it or set `torch=False`.')
            print('Falling back to numpy implementation.')
            torch = False
    if operator == 'median':
        if torch:
            operator_func = torch.nanmedian
        else:
            operator_func = np.nanmedian
    elif operator == 'mean':
        if torch:
            operator_func = torch.nanmean
        else:
            operator_func = np.nanmean
    else:
        raise ValueError('Operator must be mean or median.')
    if size % 2 == 0:
        raise ValueError("Window_size must be odd")
    if isinstance(input_image, str):
        if not input_image.endswith('.fits'):
            input_image+='.fits'
        im = fits.getdata(input_image, ext)
    else:
        im = input_image
    if isinstance(mask, str):
        if not mask.endswith('.fits'):
            mask+='.fits'
        mask = fits.getdata(mask, ext)
        mask = np.array(mask, dtype=bool)
    else:
        mask = np.array(mask, dtype=bool)
    if np.isnan(mask).any():
        if verbose:
            print('Mask contained NaNs! NaNs in mask are ignored (only pixels with value 1 are infilled).')
        mask[np.isnan(mask)] = 0
    output = np.copy(im)
    output[mask] = np.nan
    # Fix byte order and convert safely -- set to torch Tensors
    if torch:
        if isinstance(output, np.ndarray) and output.dtype.byteorder not in ('=', '|'):
            output = output.astype(output.dtype.newbyteorder('='))
        if isinstance(mask, np.ndarray) and mask.dtype.byteorder not in ('=', '|'):
            mask = mask.astype(mask.dtype.newbyteorder('='))

        output = torch.from_numpy(output).to(device='cpu', dtype=torch.float32)
        mask = torch.from_numpy(mask).to(device='cpu', dtype=torch.bool)
    pad_width = size // 2
    counter = 1
    if verbose:
        print('Starting Masked Pixel Fill.')
    while np.isnan(output).any():
        if verbose:
            print(f'On iteration {counter} | Masked pixels remaining: {np.isnan(output).sum()}')
        if torch:
            output = process_masked_pixels_torch(input_image=torch.tensor(output), pad_width=pad_width,operator_func=operator_func).cpu().numpy()
        else:
            output = process_masked_pixels(input_image=output, pad_width=pad_width, operator_func=operator_func)
        if writesteps:
            fits.writeto(f"_iter_{counter}.fits", output, overwrite=True)
            if verbose:
                print(f'Intermediate fits written to: {f"_iter_{counter}.fits"}.')
        counter += 1

    if verbose:
        print('Pixel replacement complete.')
    output1 = np.copy(output)       
    if smooth:
        if verbose:
            print('Boxcar smoothing the masked areas.')
        if torch:
            smoothed_output = process_masked_pixels_torch(input_image=torch.tensor(output), pad_width=pad_width, mask=mask,
                                                          operator_func=torch.nanmean).cpu().numpy()
        else:
            smoothed_output = process_masked_pixels(input_image=output, pad_width=pad_width, mask=mask,
                                                    operator_func=np.nanmean)
        if verbose:
            print('Smoothing complete.')

    if output_file is not None:
        if not output_file.endswith('.fits'):
            output_file +='.fits'
        if smooth:
            header = fits.Header() 
            header['EXT0'] = 'Filled Smoothed Image'
            header['EXT1'] = 'Filled Image (no smoothing)'
            hdu0 = fits.PrimaryHDU(smoothed_output,header=header)
            hdu1 = fits.ImageHDU(output1)
            hdul = fits.HDUList([hdu0,hdu1])
            hdul.writeto(output_file,overwrite=True)
        else:
            hdu = fits.PrimaryHDU(output1)
            hdu.writeto(output_file,overwrite=True)
        if verbose:
            print(f'Output written to: {output_file}')
    if smooth:
        return smoothed_output, output1
    else:
        return output1,None


def cli():
    parser = argparse.ArgumentParser()
    # Define command line arguments
    parser.add_argument("input", help="input image", type=str)
    parser.add_argument("mask", help="mask image, with values 0 = good, 1 = bad", type=str)
    parser.add_argument("output", help="output image", type=str)
    parser.add_argument("-e", "--extension",help="fits extension of data",type=int)
    parser.add_argument("-v", "--verbose", help="print actions", action="store_true")
    parser.add_argument("-s", "--size", help="scale of median filter (default = 3)", type=int)
    parser.add_argument("-o", "--operator", help="replace pixels with mean or median (default = median)", type=str)
    parser.add_argument("-n", "--nosmooth", help="omit boxcar smoothing at the end (default = False)", action="store_true")
    parser.add_argument("-w", "--writesteps", help="write result after each iteration, as _iter_#.fits", action="store_true")
    args = parser.parse_args()
    ext = args.extension if args.extension else 0 
    size = args.size if args.size and args.size>2 else 3
    operator = args.operator if args.operator and args.operator in ['mean','median'] else 'median'
    #nosmooth = args.nosmooth if args.nosmooth else False 
    smooth = not args.nosmooth
    print(smooth)
    writesteps = args.writesteps if args.writesteps else False
    output_file = args.output
    verbose = args.verbose if args.verbose else False
    result1, result2 = maskfill(input_image=args.input,
                                mask = args.mask,
                                ext = ext,
                                size=size,
                                operator=operator,
                                smooth=smooth,
                                writesteps=writesteps,
                                output_file=output_file,
                                verbose = verbose)
    
    

__version__ = "1.1.1"
if __name__ == "__main__":
    cli()
        

