import torch
import pytest
from maskfill import find_nan_indices_torch

class TestFindNanIndicesTorch:
    """Test suite for find_nan_indices_torch function"""

    def test_basic_functionality(self):
        """Test basic functionality with a simple case"""
        # Create a 5x5 tensor with NaN in the center and valid values around it
        arr = torch.ones((5, 5), dtype=torch.float64)
        arr[2, 2] = float('nan')  # Center pixel is NaN

        result = find_nan_indices_torch(arr)

        # Should find the center pixel as it has non-NaN neighbors
        expected = torch.tensor([[2, 2]], dtype=torch.long)
        assert torch.equal(result, expected), f"Expected {expected}, got {result}"

    def test_isolated_nan(self):
        """Test that isolated NaNs (no non-NaN neighbors) are not found"""
        # Create tensor with isolated NaN (surrounded by NaNs)
        arr = torch.full((5, 5), float('nan'), dtype=torch.float64)
        arr[2, 2] = float('nan')  # This NaN has no non-NaN neighbors

        result = find_nan_indices_torch(arr)

        # Should find no indices since the NaN has no non-NaN neighbors
        assert len(result) == 0, f"Expected empty result, got {result}"

    def test_multiple_nans_with_neighbors(self):
        """Test multiple NaNs that have non-NaN neighbors"""
        arr = torch.ones((5, 5), dtype=torch.float64)
        arr[1, 1] = float('nan')  # Has neighbors
        arr[1, 2] = float('nan')  # Has neighbors
        arr[3, 3] = float('nan')  # Has neighbors

        result = find_nan_indices_torch(arr)

        # Should find all three NaN positions
        expected_positions = {(1, 1), (1, 2), (3, 3)}
        result_positions = {(int(r[0]), int(r[1])) for r in result}

        assert result_positions == expected_positions, f"Expected {expected_positions}, got {result_positions}"

    def test_edge_nans(self):
        """Test NaNs at edges of the tensor"""
        arr = torch.ones((4, 4), dtype=torch.float64)
        arr[0, 0] = float('nan')  # Corner
        arr[0, 2] = float('nan')  # Edge
        arr[2, 0] = float('nan')  # Edge

        result = find_nan_indices_torch(arr)

        # All edge NaNs should be found as they have non-NaN neighbors
        expected_positions = {(0, 0), (0, 2), (2, 0)}
        result_positions = {(int(r[0]), int(r[1])) for r in result}

        assert result_positions == expected_positions, f"Expected {expected_positions}, got {result_positions}"

    def test_no_nans(self):
        """Test tensor with no NaNs"""
        arr = torch.ones((5, 5), dtype=torch.float64)

        result = find_nan_indices_torch(arr)

        assert len(result) == 0, f"Expected empty result for tensor with no NaNs, got {result}"

    def test_all_nans(self):
        """Test tensor with all NaNs"""
        arr = torch.full((5, 5), float('nan'), dtype=torch.float64)

        result = find_nan_indices_torch(arr)

        assert len(result) == 0, f"Expected empty result for all-NaN tensor, got {result}"

    def test_window_size_3(self):
        """Test with explicit window_size=3 (3x3 neighborhood)"""
        arr = torch.ones((5, 5), dtype=torch.float64)
        arr[2, 2] = float('nan')

        result = find_nan_indices_torch(arr, window_size=3)

        expected = torch.tensor([[2, 2]], dtype=torch.long)
        assert torch.equal(result, expected)


    def test_different_dtypes(self):
        """Test with different tensor dtypes"""
        for dtype in [torch.float32, torch.float64]:
            arr = torch.ones((3, 3), dtype=dtype)
            arr[1, 1] = float('nan')

            result = find_nan_indices_torch(arr)

            expected = torch.tensor([[1, 1]], dtype=torch.long)
            assert torch.equal(result, expected), f"Failed for dtype {dtype}"

    def test_gpu_compatibility(self):
        """Test GPU compatibility if CUDA is available"""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")

        arr = torch.ones((5, 5), dtype=torch.float64, device='cuda')
        arr[2, 2] = float('nan')

        result = find_nan_indices_torch(arr)

        # Result should be on the same device
        assert result.device.type == 'cuda'

        expected = torch.tensor([[2, 2]], dtype=torch.long, device='cuda')
        assert torch.equal(result, expected)

    def test_invalid_window_size(self):
        """Test that even window sizes raise ValueError"""
        arr = torch.ones((5, 5), dtype=torch.float64)

        with pytest.raises(ValueError, match="Window_size must be odd"):
            find_nan_indices_torch(arr, window_size=4)

        with pytest.raises(ValueError, match="Window_size must be odd"):
            find_nan_indices_torch(arr, window_size=2)

    def test_complex_pattern(self):
        """Test with a more complex NaN pattern"""
        arr = torch.ones((6, 6), dtype=torch.float64)

        # Create a cross pattern of NaNs
        arr[2, :] = float('nan')  # Horizontal line
        arr[:, 2] = float('nan')  # Vertical line

        result = find_nan_indices_torch(arr)

        # Only the NaNs that have non-NaN neighbors should be found
        # The completely isolated center intersection might not be found
        # depending on the exact pattern, but edge NaNs should be found
        assert len(result) > 0, "Should find some NaNs with non-NaN neighbors"

        # Verify all results are actually NaN positions
        for idx in result:
            y, x = int(idx[0]), int(idx[1])
            assert torch.isnan(arr[y, x]), f"Index ({y}, {x}) should be NaN"

    def test_single_pixel_tensor(self):
        """Test edge case with 1x1 tensor"""
        arr = torch.tensor([[float('nan')]], dtype=torch.float64)

        result = find_nan_indices_torch(arr)

        # Single NaN pixel has no neighbors, so should not be found
        assert len(result) == 0

    def test_output_shape(self):
        """Test that output shape is correct"""
        arr = torch.ones((5, 5), dtype=torch.float64)
        arr[1, 1] = float('nan')
        arr[2, 2] = float('nan')

        result = find_nan_indices_torch(arr)

        # Should return tensor of shape (N, 2) where N is number of qualifying NaNs
        assert result.dim() == 2, f"Expected 2D tensor, got shape {result.shape}"
        assert result.shape[1] == 2, f"Expected second dimension to be 2, got shape {result.shape}"
        assert result.dtype == torch.long, f"Expected long dtype, got {result.dtype}"

    def test_consistency_across_devices(self):
        """Test that results are consistent between CPU and GPU"""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")

        # Create test tensor on CPU
        arr_cpu = torch.ones((5, 5), dtype=torch.float64)
        arr_cpu[1, 1] = float('nan')
        arr_cpu[2, 3] = float('nan')

        # Copy to GPU
        arr_gpu = arr_cpu.cuda()

        # Get results from both devices
        result_cpu = find_nan_indices_torch(arr_cpu)
        result_gpu = find_nan_indices_torch(arr_gpu)

        # Results should be the same (after moving to same device)
        assert torch.equal(result_cpu, result_gpu.cpu()), "Results should be consistent across devices"


