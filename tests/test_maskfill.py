
from maskfill import find_nan_indices, process_masked_pixels, maskfill 
import numpy as np 
from astropy.io import fits 
# Test Suite for the maskfill code to ensure behavior is as expected. 


def test_nanfinder_1():
    """
    all eight nans should be returned as all border the pixel with value 1.
    """
    input_array = np.array([[np.nan,np.nan,np.nan],
                            [np.nan,   1  ,np.nan],
                            [np.nan,np.nan,np.nan]])
    expected = np.array([[0,0],
                        [0,1],
                        [0,2],
                        [1,0],
                        [1,2],
                        [2,0],
                        [2,1],
                        [2,2]])
    out_ind = find_nan_indices(input_array)
    np.testing.assert_equal(out_ind,expected)


def test_nanfinder_2():
    """
    Only the three nans bordering the 1.0 in the corner should be found
    """
    input_array = np.array([[1.0   ,np.nan,np.nan],
                            [np.nan,np.nan,np.nan],
                            [np.nan,np.nan,np.nan]])
    expected = np.array([[0,1],
                        [1,0],
                        [1,1]])
    out_ind = find_nan_indices(input_array)
    np.testing.assert_equal(out_ind,expected)


def test_nanfinder_3():
    """
    expanding window to 5, all nans should be found.
    """
    input_array = np.array([[1.0   ,np.nan,np.nan],
                            [np.nan,np.nan,np.nan],
                            [np.nan,np.nan,np.nan]])
    expected = np.array([
                        [0,1],
                        [0,2],
                        [1,0],
                        [1,1],
                        [1,2],
                        [2,0],
                        [2,1],
                        [2,2]])
    out_ind = find_nan_indices(input_array,window_size=5)
    np.testing.assert_equal(out_ind,expected)


def test_nanfinder_4():
    """
    For our contiguous mask, the nan finder should return the outer layer only, 
    assuming our normal 3x3 window. (i.e., the two middle nans, at [2,2] and [2,3]
    should not be returned in the list.)
    """
    input_array = np.array([[1,   1  ,   1  ,  1   ,  1   ,1],
                            [1,np.nan,np.nan,np.nan,np.nan,1],
                            [1,np.nan,np.nan,np.nan,np.nan,1],
                            [1,np.nan,np.nan,np.nan,np.nan,1],
                            [1,   1  ,   1  ,  1   ,  1   ,1]])
    expected = np.array([
                        [1,1],
                        [1,2],
                        [1,3],
                        [1,4],
                        [2,1],
                        [2,4],
                        [3,1],
                        [3,2],
                        [3,3],
                        [3,4]])
    out_ind = find_nan_indices(input_array)
    np.testing.assert_equal(out_ind,expected)

def test_nanfinder_5():
    """
    Here the column 1 and column 4 should be returned.
    """
    input_array = np.array([[1,np.nan,np.nan,np.nan,np.nan,1],
                            [1,np.nan,np.nan,np.nan,np.nan,1],
                            [1,np.nan,np.nan,np.nan,np.nan,1],
                            [1,np.nan,np.nan,np.nan,np.nan,1],
                            [1,np.nan,np.nan,np.nan,np.nan,1]])
    expected = np.array([[0,1],
                        [0,4],
                        [1,1],
                        [1,4],
                        [2,1],
                        [2,4],
                        [3,1],
                        [3,4],
                        [4,1],
                        [4,4]])
    out_ind = find_nan_indices(input_array)
    np.testing.assert_equal(out_ind,expected)

def test_nanfinder_6():
    """
    Here the the layers around the 1s should be returned.
    """
    input_array = np.array([[np.nan,np.nan,np.nan,np.nan,np.nan,np.nan],
                            [np.nan,1     ,np.nan,np.nan,np.nan,np.nan],
                            [np.nan,np.nan,np.nan,np.nan,np.nan,np.nan],
                            [np.nan,np.nan,np.nan,np.nan,1     ,np.nan],
                            [np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]])
    expected = np.array([[0,0],
                         [0,1],
                         [0,2],
                         [1,0],
                         [1,2],
                         [2,0],
                         [2,1],
                         [2,2],
                         [2,3],
                         [2,4],
                         [2,5],
                         [3,3],
                         [3,5],
                         [4,3],
                         [4,4],
                         [4,5]])
    out_ind = find_nan_indices(input_array)
    np.testing.assert_equal(out_ind,expected)



def test_proccess_1(): 
    """ 
    Test infilling. Here, should get a column of ones inside.
    """
    input_array = np.array([[1,np.nan,np.nan,np.nan,np.nan,1],
                            [1,np.nan,np.nan,np.nan,np.nan,1],
                            [1,np.nan,np.nan,np.nan,np.nan,1],
                            [1,np.nan,np.nan,np.nan,np.nan,1],
                            [1,np.nan,np.nan,np.nan,np.nan,1]])
    expected    = np.array([[1,1,np.nan,np.nan,1,1],
                            [1,1,np.nan,np.nan,1,1],
                            [1,1,np.nan,np.nan,1,1],
                            [1,1,np.nan,np.nan,1,1],
                            [1,1,np.nan,np.nan,1,1]])
    
    out = process_masked_pixels(input_array,pad_width=1)
    np.testing.assert_equal(out,expected)

def test_process_2():
    """ 
    Test infilling. Here, 8 pix around each 1 should be filled with 1.
    """
    input_array = np.array([[np.nan,np.nan,np.nan,np.nan,np.nan,np.nan],
                            [np.nan,1     ,np.nan,np.nan,np.nan,np.nan],
                            [np.nan,np.nan,np.nan,np.nan,np.nan,np.nan],
                            [np.nan,np.nan,np.nan,np.nan,1     ,np.nan],
                            [np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]])
    expected    = np.array([[1,1,1,np.nan,np.nan,np.nan],
                            [1,1,1,np.nan,np.nan,np.nan],
                            [1,1,1,1,1,1],
                            [np.nan,np.nan,np.nan,1,1     ,1],
                            [np.nan,np.nan,np.nan,1,1,1]])
    out = process_masked_pixels(input_array,pad_width=1)
    np.testing.assert_equal(out,expected)

def test_proccess_3(): 
    """ 
    Test infilling. Here, column will reflect the mean of 1,3, vs 1,1,3
    """
    input_array = np.array([[1,np.nan,np.nan,np.nan,np.nan,1],
                            [3,np.nan,np.nan,np.nan,np.nan,3],
                            [1,np.nan,np.nan,np.nan,np.nan,1],
                            [1,np.nan,np.nan,np.nan,np.nan,1],
                            [1,np.nan,np.nan,np.nan,np.nan,1]])
    expected    = np.array([[1,2,np.nan,np.nan,2,1],
                            [3,1,np.nan,np.nan,1,3],
                            [1,1,np.nan,np.nan,1,1],
                            [1,1,np.nan,np.nan,1,1],
                            [1,1,np.nan,np.nan,1,1]])

    out = process_masked_pixels(input_array,pad_width=1,operator_func=np.nanmedian)
    np.testing.assert_equal(out,expected)


def test_proccess_4(): 
    """ 
    Confirm we can pass a mask and use that and *not* the NaNs to do a mean fill.
    """
    input_array = np.array([[np.nan,np.nan,np.nan,np.nan,np.nan,1],
                            [3     ,1,np.nan,np.nan,np.nan,3],
                            [1     ,np.nan,np.nan,np.nan,np.nan,1],
                            [1,np.nan,np.nan,np.nan,1,1],
                            [1,np.nan,np.nan,np.nan,np.nan,1]])
    mask =        np.array([[1,0,0,0,0,0],
                            [0,0,0,0,0,0],
                            [0,0,0,0,0,0],
                            [0,0,0,0,0,0],
                            [0,0,0,0,0,1]])
    expected    = np.array([[2,np.nan,np.nan,np.nan,np.nan,1],
                            [3,1,np.nan,np.nan,np.nan,3],
                            [1,np.nan,np.nan,np.nan,np.nan,1],
                            [1,np.nan,np.nan,np.nan,1,1],
                            [1,np.nan,np.nan,np.nan,np.nan,1]])

    out = process_masked_pixels(input_array,pad_width=1,mask=mask,operator_func=np.nanmean)
    np.testing.assert_equal(out,expected)

def test_maskfill_1():
    """ 
    Test that maskfill's output for the smoothed and not smoothed versions matches 
    an output from the original implementation
    """
    orig = fits.getdata('default.fits')
    new_sm,new = maskfill(  '../example_synthetic/synth_im.fits',
                            '../example_synthetic/synth_mask.fits')
    
    np.testing.assert_equal(orig,new_sm)


