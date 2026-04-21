"""FastAPI application for Relay Lens HSI visualization."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .routes_files import router as files_router
from .routes_viz import router as viz_router

app = FastAPI(title="Relay Lens", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Session-ID"],
)

app.include_router(files_router, prefix="/api/files", tags=["files"])
app.include_router(viz_router, prefix="/api/viz", tags=["visualization"])

# Serve built frontend in production
DIST_DIR = Path(__file__).resolve().parent.parent / "dist"
if DIST_DIR.exists():
    app.mount("/assets", StaticFiles(directory=DIST_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """SPA fallback: serve index.html for any non-API, non-asset path."""
        file_path = (DIST_DIR / full_path).resolve()
        if file_path.is_relative_to(DIST_DIR) and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(DIST_DIR / "index.html")
