"""File management with lazy loading and LRU caching.

Key design decisions:
- whosmat() for metadata: reads shape/dtype without loading data (<1ms)
- loadmat(variable_names=[key]) for on-demand loading: only loads requested key
- LRU cache with max entries to bound memory usage
"""

import uuid
import shutil
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import scipy.io as sio


INPUT_DIR = Path(__file__).resolve().parent.parent / "input"
MASK_DIR = Path(__file__).resolve().parent.parent / "mask"


def classify_key(shape: tuple[int, ...]) -> str:
    """Classify a .mat key by its shape into a visualization type."""
    ndim = len(shape)
    if ndim == 4 and shape[-1] in (28, 31):
        return "hsi_cube_batch"
    if ndim == 3 and shape[-1] in (28, 31):
        return "hsi_cube"
    if ndim == 1 or (ndim == 2 and min(shape) == 1):
        return "metric_array"
    if ndim == 2 and shape[0] > 1 and shape[1] > 1:
        return "image_2d"
    return "unknown"


@dataclass
class KeyInfo:
    name: str
    shape: tuple[int, ...]
    dtype: str
    data_type: str  # hsi_cube_batch | hsi_cube | metric_array | image_2d | unknown


@dataclass
class FileEntry:
    file_id: str
    filename: str
    path: Path
    keys: list[KeyInfo] = field(default_factory=list)


class DataCache:
    """Simple LRU cache for loaded numpy arrays."""

    def __init__(self, max_entries: int = 20):
        self._store: OrderedDict[str, np.ndarray] = OrderedDict()
        self._max = max_entries

    def get(self, key: str) -> np.ndarray | None:
        if key in self._store:
            self._store.move_to_end(key)
            return self._store[key]
        return None

    def put(self, key: str, data: np.ndarray) -> None:
        if key in self._store:
            self._store.move_to_end(key)
            return
        if len(self._store) >= self._max:
            self._store.popitem(last=False)
        self._store[key] = data

    def evict_file(self, file_id: str) -> None:
        """Remove all cached data for a given file."""
        keys_to_remove = [k for k in self._store if k.startswith(f"{file_id}:")]
        for k in keys_to_remove:
            del self._store[k]


class FileManager:
    """Manages .mat file registration, metadata scanning, and lazy data loading."""

    def __init__(self):
        self._files: dict[str, FileEntry] = {}
        self._cache = DataCache()
        self._mask: np.ndarray | None = None
        self._mask_filename: str | None = None

    def scan_file(self, path: Path) -> FileEntry:
        """Register a .mat file: read metadata without loading data."""
        # Check if already registered by path
        for entry in self._files.values():
            if entry.path.resolve() == path.resolve():
                return entry

        entries = sio.whosmat(str(path))
        keys = []
        for name, shape, dtype in entries:
            data_type = classify_key(shape)
            keys.append(KeyInfo(name=name, shape=shape, dtype=str(dtype), data_type=data_type))

        file_id = uuid.uuid4().hex[:12]
        entry = FileEntry(file_id=file_id, filename=path.name, path=path, keys=keys)
        self._files[file_id] = entry
        return entry

    def scan_local_dir(self) -> list[FileEntry]:
        """Scan the input/ directory for .mat files."""
        if not INPUT_DIR.exists():
            return []
        results = []
        for p in sorted(INPUT_DIR.glob("*.mat")):
            results.append(self.scan_file(p))
        return results

    def save_uploaded(self, filename: str, content: bytes) -> Path:
        """Save an uploaded file to the input/ directory."""
        INPUT_DIR.mkdir(exist_ok=True)
        dest = INPUT_DIR / filename
        dest.write_bytes(content)
        return dest

    def get_file(self, file_id: str) -> FileEntry:
        if file_id not in self._files:
            raise KeyError(f"File not found: {file_id}")
        return self._files[file_id]

    def list_files(self) -> list[FileEntry]:
        return list(self._files.values())

    def remove_file(self, file_id: str, delete_from_disk: bool = True) -> None:
        entry = self._files[file_id]
        self._cache.evict_file(file_id)
        del self._files[file_id]
        # deletion should be restricted to uploaded files only
        if delete_from_disk and entry.path.resolve().is_relative_to(INPUT_DIR.resolve()):
            entry.path.unlink(missing_ok=True)

    def load_key(self, file_id: str, key_name: str) -> np.ndarray:
        """Load a specific key from a .mat file, with LRU caching."""
        cache_key = f"{file_id}:{key_name}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        entry = self.get_file(file_id)
        mat = sio.loadmat(str(entry.path), variable_names=[key_name])
        if key_name not in mat:
            raise KeyError(f"Key '{key_name}' not found in {entry.filename}")
        data = mat[key_name]
        self._cache.put(cache_key, data)
        return data

    def get_common_keys(self) -> list[KeyInfo]:
        """Extract keys that exist in ALL loaded files with matching data types."""
        file_list = list(self._files.values())
        if not file_list:
            return []

        # Start with first file's keys (name -> KeyInfo)
        common: dict[str, KeyInfo] = {k.name: k for k in file_list[0].keys}

        for entry in file_list[1:]:
            entry_map = {k.name: k for k in entry.keys}
            common = {
                name: ki
                for name, ki in common.items()
                if name in entry_map and entry_map[name].data_type == ki.data_type
            }

        return list(common.values())

    def get_file_info(self, file_id: str) -> dict:
        """Get detailed file structure using load_raw_data."""
        from hsi_utils.datasets import load_raw_data

        entry = self.get_file(file_id)
        info = load_raw_data(entry.path)
        return info["metadata"]

    # -- Mask management --

    def load_mask_file(self, path: Path, key: str | None = None) -> None:
        """Load a 2D mask from a .mat file.

        If key is None, auto-detect the first 2D array.
        """
        mat = sio.loadmat(str(path))
        if key:
            if key not in mat:
                raise KeyError(f"Key '{key}' not found in {path.name}")
            self._mask = np.asarray(mat[key], dtype=np.float64)
        else:
            # Auto-detect first 2D array
            for k, v in mat.items():
                if k.startswith("_"):
                    continue
                arr = np.asarray(v)
                if arr.ndim == 2 and arr.shape[0] > 1 and arr.shape[1] > 1:
                    self._mask = arr.astype(np.float64)
                    key = k
                    break
            else:
                raise ValueError(f"No 2D array found in {path.name}")
        self._mask_filename = path.name

    def scan_mask_dir(self) -> bool:
        """Scan mask/ directory and load the first .mat file found."""
        if not MASK_DIR.exists():
            return False
        for p in sorted(MASK_DIR.glob("*.mat")):
            self.load_mask_file(p)
            return True
        return False

    def save_uploaded_mask(self, filename: str, content: bytes) -> None:
        """Save and load an uploaded mask file."""
        MASK_DIR.mkdir(exist_ok=True)
        dest = MASK_DIR / filename
        dest.write_bytes(content)
        self.load_mask_file(dest)

    def get_mask(self) -> np.ndarray:
        """Return the currently loaded mask, or raise."""
        if self._mask is None:
            raise ValueError("No mask loaded")
        return self._mask

    def mask_status(self) -> dict:
        """Return current mask info."""
        if self._mask is None:
            return {"loaded": False}
        return {
            "loaded": True,
            "filename": self._mask_filename,
            "shape": list(self._mask.shape),
        }


# Module-level singleton
file_manager = FileManager()
