"""Visualization functions wrapping hsi-utils.

Pure functions: numpy in, PIL Image out. No state, no side effects.
"""

import numpy as np
from PIL import Image

from hsi_utils.rendering import (
    hsi_to_rgb,
    colorize_channel,
    draw_magnified_inset,
    InsetPosition,
    render_measurement,
)
from hsi_utils.rendering._wavelength_data import get_wavelengths
from hsi_utils.plotting import draw_plot, PlotInput, draw_spectral_density, SpectralInput


def _normalize_cube(cube: np.ndarray, original_dtype: np.dtype) -> np.ndarray:
    """Normalize cube values to [0, 1] if not already in range.

    Integer dtypes: divide by dtype max (e.g. uint16 -> /65535).
    Float dtypes outside [0, 1]: divide by data max.
    Then clip to [0, 1].
    """
    if np.issubdtype(original_dtype, np.integer):
        cube = cube / np.float64(np.iinfo(original_dtype).max)
    elif cube.max() > 1.0 or cube.min() < 0.0:
        max_val = cube.max()
        if max_val > 0:
            cube = cube / max_val
    return np.clip(cube, 0.0, 1.0)


def get_scene(data: np.ndarray, scene: int) -> np.ndarray:
    """Extract a single scene (H, W, C) from possibly batched data."""
    original_dtype = data.dtype
    if data.ndim == 4:
        if scene < 0 or scene >= data.shape[0]:
            raise IndexError(f"Scene {scene} out of range [0, {data.shape[0]})")
        cube = data[scene].astype(np.float64)
    elif data.ndim == 3:
        if scene != 0:
            raise IndexError(f"Single cube has no scene index {scene}")
        cube = data.astype(np.float64)
    else:
        raise ValueError(f"Expected 3D or 4D array, got {data.ndim}D")
    return _normalize_cube(cube, original_dtype)


def render_rgb(cube: np.ndarray) -> Image.Image:
    """HSI cube (H, W, C) -> RGB image."""
    wavelengths = get_wavelengths(cube.shape[2])
    rgb = hsi_to_rgb(cube, wavelengths=wavelengths)
    return Image.fromarray(rgb)


def render_colorized(cube: np.ndarray, channel: int) -> Image.Image:
    """Single channel pseudo-colored by its wavelength."""
    wl = float(get_wavelengths(cube.shape[2])[channel])
    colored = colorize_channel(np.clip(cube[:, :, channel], 0, 1), wl)
    return Image.fromarray(colored)


def render_rgb_error_map(
    pred: np.ndarray, truth: np.ndarray, scale: float = 5.0
) -> Image.Image:
    """RGB error map: |rgb(pred) - rgb(truth)| * scale."""
    wavelengths = get_wavelengths(pred.shape[2])
    rgb_pred = hsi_to_rgb(pred, wavelengths=wavelengths).astype(np.float64)
    rgb_truth = hsi_to_rgb(truth, wavelengths=wavelengths).astype(np.float64)
    diff = np.abs(rgb_pred - rgb_truth) * scale
    return Image.fromarray(np.clip(np.round(diff), 0, 255).astype(np.uint8))


def render_channel_error_map(
    pred: np.ndarray, truth: np.ndarray, channel: int, scale: float = 5.0
) -> Image.Image:
    """Per-channel colorized error map."""
    wl = float(get_wavelengths(pred.shape[2])[channel])
    pred_c = colorize_channel(np.clip(pred[:, :, channel], 0, 1), wl)
    truth_c = colorize_channel(np.clip(truth[:, :, channel], 0, 1), wl)
    diff = np.abs(pred_c.astype(np.float64) - truth_c.astype(np.float64)) * scale
    return Image.fromarray(np.clip(np.round(diff), 0, 255).astype(np.uint8))


def render_magnified(
    cube: np.ndarray,
    channel: int,
    roi: tuple[int, int, int, int],
    position: InsetPosition = InsetPosition.BOTTOM_RIGHT,
) -> Image.Image:
    """Colorized channel with magnified ROI inset overlay."""
    wl = float(get_wavelengths(cube.shape[2])[channel])
    colored = colorize_channel(np.clip(cube[:, :, channel], 0, 1), wl)
    result = draw_magnified_inset(colored, roi, inset_position=position)
    return Image.fromarray(result)


def render_metrics(data_dict: dict[str, np.ndarray]) -> Image.Image:
    """Line chart for 1D metric arrays (PSNR, SSIM, etc.)."""
    plots = []
    for label, arr in data_dict.items():
        flat = arr.flatten().tolist()
        plots.append(PlotInput(data=flat, identifier=label, show_max=True, show_min=True))

    return draw_plot(
        left_axis_plots=plots,
        left_axis_label="Value",
        x_axis_label="Scene Index",
        title="Metrics",
    )


def render_spectral_density(
    inputs: list[SpectralInput],
    roi: tuple[int, int, int, int],
) -> Image.Image:
    """Spectral density curves for multiple cubes over a ROI."""
    return draw_spectral_density(inputs=inputs, roi=roi)


# -- Measurement (CASSI forward model, numpy) --


def _shift_np(x: np.ndarray, step: int = 2) -> np.ndarray:
    """Simulate CASSI spectral dispersion shift (numpy).

    Args:
        x: (C, H, W) array.

    Returns:
        (C, H, W + (C-1)*step) shifted array.
    """
    C, H, W = x.shape
    out = np.zeros((C, H, W + (C - 1) * step), dtype=x.dtype)
    for i in range(C):
        out[i, :, step * i : step * i + W] = x[i]
    return out


def compute_measurement(
    cube: np.ndarray, mask: np.ndarray, step: int = 2
) -> Image.Image:
    """CASSI forward model: cube + mask -> compressed measurement grayscale image.

    Args:
        cube: (H, W, C) single-scene HSI cube.
        mask: (H, W) coded aperture mask.
        step: Dispersion shift step.

    Returns:
        Grayscale PIL Image of shape (H, W_shifted).
    """
    H, W, C = cube.shape
    x = cube.transpose(2, 0, 1)  # (C, H, W)
    x_shifted = _shift_np(x, step)

    mask_3d = np.broadcast_to(mask[None, :, :], (C, H, W)).copy()
    mask_shifted = _shift_np(mask_3d, step)

    meas = np.sum(x_shifted * mask_shifted, axis=0) / C * 2  # (H, W_shifted)

    gray = render_measurement(meas)
    return Image.fromarray(gray)
