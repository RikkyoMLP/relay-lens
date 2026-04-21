"""Visualization API routes. Each endpoint returns image/png.

Viz endpoints use session_id as a query parameter (not a header) because
browser <img src="..."> tags cannot set custom HTTP headers.
"""

import io

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from PIL import Image

from .file_manager import FileManager, get_session_manager
from . import viz

router = APIRouter()


def _get_fm(session_id: str = Query(...)) -> FileManager:
    return get_session_manager(session_id)


def _image_response(img: Image.Image) -> StreamingResponse:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


def _load_scene(fm: FileManager, file_id: str, key: str, scene: int):
    """Load data and extract a single scene cube."""
    try:
        data = fm.load_key(file_id, key)
    except KeyError as e:
        raise HTTPException(404, str(e))
    try:
        return viz.get_scene(data, scene)
    except (IndexError, ValueError) as e:
        raise HTTPException(400, str(e))


@router.get("/rgb")
async def viz_rgb(file_id: str, key: str, scene: int = 0, fm: FileManager = Depends(_get_fm)):
    cube = _load_scene(fm, file_id, key, scene)
    img = viz.render_rgb(cube)
    return _image_response(img)


@router.get("/colorized")
async def viz_colorized(
    file_id: str, key: str, scene: int = 0, channel: int = 2,
    fm: FileManager = Depends(_get_fm),
):
    cube = _load_scene(fm, file_id, key, scene)
    try:
        img = viz.render_colorized(cube, channel)
    except IndexError:
        raise HTTPException(400, f"Channel {channel} out of range")
    return _image_response(img)


@router.get("/error-map")
async def viz_error_map(
    file_id: str,
    pred_key: str,
    truth_key: str,
    scene: int = 0,
    channel: int | None = None,
    scale: float = 5.0,
    fm: FileManager = Depends(_get_fm),
):
    """Error map. If channel is given, returns per-channel colorized diff.
    Otherwise returns RGB diff."""
    pred_cube = _load_scene(fm, file_id, pred_key, scene)
    truth_cube = _load_scene(fm, file_id, truth_key, scene)
    if channel is not None:
        img = viz.render_channel_error_map(pred_cube, truth_cube, channel, scale)
    else:
        img = viz.render_rgb_error_map(pred_cube, truth_cube, scale)
    return _image_response(img)


@router.get("/magnified")
async def viz_magnified(
    file_id: str,
    key: str,
    scene: int = 0,
    channel: int = 2,
    roi_x: int = 100,
    roi_y: int = 80,
    roi_w: int = 40,
    roi_h: int = 40,
    fm: FileManager = Depends(_get_fm),
):
    cube = _load_scene(fm, file_id, key, scene)
    try:
        img = viz.render_magnified(cube, channel, (roi_x, roi_y, roi_w, roi_h))
    except (IndexError, ValueError) as e:
        raise HTTPException(400, str(e))
    return _image_response(img)


@router.get("/metrics")
async def viz_metrics(
    file_id: str,
    keys: str = Query(..., description="Comma-separated key names"),
    fm: FileManager = Depends(_get_fm),
):
    """Render a line chart for 1D metric arrays."""
    key_list = [k.strip() for k in keys.split(",") if k.strip()]
    if not key_list:
        raise HTTPException(400, "No keys specified")
    data_dict = {}
    for k in key_list:
        try:
            data_dict[k] = fm.load_key(file_id, k)
        except KeyError as e:
            raise HTTPException(404, str(e))
    img = viz.render_metrics(data_dict)
    return _image_response(img)


@router.get("/spectral-density")
async def viz_spectral_density(
    sources: str = Query(..., description="JSON array of source objects"),
    roi_x: int = 100,
    roi_y: int = 80,
    roi_w: int = 40,
    roi_h: int = 40,
    fm: FileManager = Depends(_get_fm),
):
    """Spectral density curves for multiple cubes over a ROI.
    sources format: [{"file_id":"..","key":"..","scene":0,"label":"..","is_gt":false}, ...]
    """
    import json
    from hsi_utils.plotting import SpectralInput

    try:
        source_list = json.loads(sources)
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid JSON in sources parameter")

    inputs = []
    for s in source_list:
        cube = _load_scene(fm, s["file_id"], s["key"], s.get("scene", 0))
        inputs.append(SpectralInput(
            cube=cube,
            label=s.get("label", f"{s['key']}"),
            is_ground_truth=s.get("is_ground_truth", False),
        ))

    roi = (roi_x, roi_y, roi_w, roi_h)
    img = viz.render_spectral_density(inputs, roi)
    return _image_response(img)


@router.get("/measurement")
async def viz_measurement(
    file_id: str, key: str, scene: int = 0,
    fm: FileManager = Depends(_get_fm),
):
    """CASSI compressed measurement: cube * shifted_mask, summed over channels."""
    cube = _load_scene(fm, file_id, key, scene)
    try:
        mask = fm.get_mask()
    except ValueError as e:
        raise HTTPException(400, str(e))
    img = viz.compute_measurement(cube, mask)
    return _image_response(img)

