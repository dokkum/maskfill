:py:mod:`maskfill.maskfill`
===========================

.. py:module:: maskfill.maskfill

.. autodoc2-docstring:: maskfill.maskfill
   :allowtitles:

Module Contents
---------------

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`find_nan_indices <maskfill.maskfill.find_nan_indices>`
     - .. autodoc2-docstring:: maskfill.maskfill.find_nan_indices
          :summary:
   * - :py:obj:`process_masked_pixels <maskfill.maskfill.process_masked_pixels>`
     - .. autodoc2-docstring:: maskfill.maskfill.process_masked_pixels
          :summary:
   * - :py:obj:`maskfill <maskfill.maskfill.maskfill>`
     - .. autodoc2-docstring:: maskfill.maskfill.maskfill
          :summary:
   * - :py:obj:`cli <maskfill.maskfill.cli>`
     - .. autodoc2-docstring:: maskfill.maskfill.cli
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`__version__ <maskfill.maskfill.__version__>`
     - .. autodoc2-docstring:: maskfill.maskfill.__version__
          :summary:

API
~~~

.. py:function:: find_nan_indices(arr: numpy.ndarray, window_size: int = 3)
   :canonical: maskfill.maskfill.find_nan_indices

   .. autodoc2-docstring:: maskfill.maskfill.find_nan_indices

.. py:function:: process_masked_pixels(input_image: numpy.ndarray, pad_width: int, mask: numpy.ndarray = None, operator_func: typing.Callable[[numpy.ndarray | float], numpy.ndarray | float] = np.nanmean)
   :canonical: maskfill.maskfill.process_masked_pixels

   .. autodoc2-docstring:: maskfill.maskfill.process_masked_pixels

.. py:function:: maskfill(input_image: typing.Union[str, numpy.ndarray], mask: typing.Union[str, numpy.ndarray], ext: int = 0, size: int = 3, operator: str = 'median', smooth: bool = True, writesteps: bool = False, output_file: str = None, verbose: bool = False)
   :canonical: maskfill.maskfill.maskfill

   .. autodoc2-docstring:: maskfill.maskfill.maskfill

.. py:function:: cli()
   :canonical: maskfill.maskfill.cli

   .. autodoc2-docstring:: maskfill.maskfill.cli

.. py:data:: __version__
   :canonical: maskfill.maskfill.__version__
   :value: '1.1.2'

   .. autodoc2-docstring:: maskfill.maskfill.__version__
