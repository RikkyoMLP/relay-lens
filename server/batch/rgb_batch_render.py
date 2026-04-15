"""Batch RGB rendering for .mat files.

Scans a directory for .mat files, loads the specified key from each,
and saves the rendered RGB image as PNG.
"""

from pathlib import Path
import os

import scipy.io as sio

from server.viz import get_scene, render_rgb


def _unified_render_rgb(mat_path: Path, key: str, output_dir: Path) -> list[Path]:
    """
    Handles either 3D and 4D (includes multiple scenes in one .mat file) HSI cube.
    Should only be used as a private function to avoid confusion with render_rgb in server.viz,
    which only handles 3D cube.
    """
    if not Path(output_dir).exists():
        os.makedirs(output_dir, exist_ok=False)
    
    mat = sio.loadmat(str(mat_path), variable_names=[key])
    if key not in mat:
        print(f"  [SKIP] key '{key}' not found in {mat_path.name}")
        return []

    data = mat[key]
    if data.ndim not in (3, 4):
        print(f"  [SKIP] unexpected ndim={data.ndim} for key '{key}' in {mat_path.name}")
        return []

    # Normalize to 4D (N, H, W, C)
    if data.ndim == 3:
        data = data[None, :, :, :]

    stem = mat_path.stem
    n = data.shape[0]
    saved = []
    for i in range(n):
        cube = get_scene(data, i)
        suffix = f"_scene{i:03d}" if n > 1 else ""
        out_path = output_dir / f"{stem}{suffix}.png"
        render_rgb(cube).save(out_path)
        saved.append(out_path)
    return saved


def scan_and_render(path: Path | str, key: str, output: Path | str | None = None) -> list[Path]:
    path = Path(path)
    output_dir = Path(output) if output else path / "rgb_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    mat_files = sorted(path.glob("*.mat"))
    if not mat_files:
        print(f"No .mat files found in {path}")
        return []

    print(f"Found {len(mat_files)} .mat files, rendering key='{key}'")
    all_saved: list[Path] = []

    for mat_path in mat_files:
        saved = _unified_render_rgb(mat_path, key, output_dir)
        for p in saved:
            print(f"  -> {p.name}")
        all_saved.extend(saved)

    print(f"Done. {len(all_saved)} images saved to {output_dir}")
    return all_saved