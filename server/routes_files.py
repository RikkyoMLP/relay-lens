"""File management API routes."""

from fastapi import APIRouter, Depends, Header, UploadFile, File, HTTPException

from .file_manager import FileManager, get_session_manager

router = APIRouter()


def _get_fm(x_session_id: str = Header(...)) -> FileManager:
    return get_session_manager(x_session_id)


def _serialize_file(entry):
    return {
        "fileId": entry.file_id,
        "filename": entry.filename,
        "keys": [
            {
                "name": k.name,
                "shape": list(k.shape),
                "dtype": k.dtype,
                "dataType": k.data_type,
            }
            for k in entry.keys
        ],
    }


@router.post("/upload")
async def upload_files(
    files: list[UploadFile] = File(...),
    fm: FileManager = Depends(_get_fm),
):
    """Upload one or more .mat files."""
    results = []
    for f in files:
        if not f.filename or not f.filename.endswith(".mat"):
            raise HTTPException(400, f"Only .mat files are accepted, got: {f.filename}")
        content = await f.read()
        path = fm.save_uploaded(f.filename, content)
        entry = fm.scan_file(path)
        results.append(_serialize_file(entry))
    return {"files": results}


@router.post("/scan-local")
async def scan_local(fm: FileManager = Depends(_get_fm)):
    """Scan the input/ directory for .mat files."""
    entries = fm.scan_local_dir()
    return {"files": [_serialize_file(e) for e in entries]}


@router.get("")
async def list_files(fm: FileManager = Depends(_get_fm)):
    """List all currently loaded files."""
    return {"files": [_serialize_file(e) for e in fm.list_files()]}


@router.get("/common-keys")
async def common_keys(fm: FileManager = Depends(_get_fm)):
    """Get keys present in ALL loaded files with matching types."""
    keys = fm.get_common_keys()
    return {
        "commonKeys": [
            {
                "name": k.name,
                "shape": list(k.shape),
                "dtype": k.dtype,
                "dataType": k.data_type,
            }
            for k in keys
        ]
    }


@router.get("/{file_id}/info")
async def file_info(file_id: str, fm: FileManager = Depends(_get_fm)):
    """Get detailed file structure (calls load_raw_data)."""
    try:
        info = fm.get_file_info(file_id)
    except KeyError:
        raise HTTPException(404, f"File not found: {file_id}")
    return {"structure": info}


@router.delete("/{file_id}")
async def delete_file(file_id: str, fm: FileManager = Depends(_get_fm)):
    """Unload a file from the registry (does not delete from disk)."""
    try:
        fm.remove_file(file_id)
    except KeyError:
        raise HTTPException(404, f"File not found: {file_id}")
    return {"ok": True}


# -- Mask management --


@router.post("/upload-mask")
async def upload_mask(
    file: UploadFile = File(...),
    fm: FileManager = Depends(_get_fm),
):
    """Upload a mask .mat file."""
    if not file.filename or not file.filename.endswith(".mat"):
        raise HTTPException(400, "Only .mat files are accepted")
    content = await file.read()
    try:
        fm.save_uploaded_mask(file.filename, content)
    except (KeyError, ValueError) as e:
        raise HTTPException(400, str(e))
    return fm.mask_status()


@router.post("/scan-mask")
async def scan_mask(fm: FileManager = Depends(_get_fm)):
    """Scan the mask/ directory for a mask file."""
    found = fm.scan_mask_dir()
    if not found:
        raise HTTPException(404, "No .mat files found in mask/ directory")
    return fm.mask_status()


@router.get("/mask-status")
async def mask_status(fm: FileManager = Depends(_get_fm)):
    """Get current mask loading status."""
    return fm.mask_status()

