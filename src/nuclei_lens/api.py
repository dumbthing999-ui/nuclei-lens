"""Optional local API; browser deployment performs analysis on-device."""

from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from . import __version__
from .core import analyze
from .raster import MAX_FILE_BYTES, decode_image, serialize

app = FastAPI(title="NucleiLens local companion", version=__version__, docs_url="/api/docs")
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])
slots = asyncio.Semaphore(2)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cache-Control"] = "no-store" if request.url.path.startswith("/api/") else "no-cache"
    return response


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": __version__, "storage": "none", "execution": "local CPU"}


@app.post("/api/analyze")
async def analyze_upload(request: Request):
    origin = request.headers.get("origin")
    if origin and origin != str(request.base_url).rstrip("/"):
        raise HTTPException(403, "Cross-origin analysis requests are not allowed.")
    # Raw bytes avoid multipart parser overhead and filename/path hazards.
    if request.headers.get("content-type", "").split(";")[0] not in {
        "application/octet-stream", "image/png", "image/tiff", "image/jpeg"
    }:
        raise HTTPException(415, "Send raw PNG, TIFF, or JPEG bytes.")
    try:
        await asyncio.wait_for(slots.acquire(), timeout=0.05)
    except TimeoutError:
        return JSONResponse({"detail": "Analysis capacity is busy. Retry shortly."}, status_code=503,
                            headers={"Retry-After": "5"})
    try:
        payload = bytearray()
        try:
            async with asyncio.timeout(5):
                async for chunk in request.stream():
                    if len(payload) + len(chunk) > MAX_FILE_BYTES:
                        raise HTTPException(413, "Image file exceeds 10 MB.")
                    payload.extend(chunk)
        except TimeoutError as exc:
            raise HTTPException(408, "Image transfer exceeded the local upload time limit.") from exc

        def compute():
            return serialize(analyze(decode_image(bytes(payload))))
        return await run_in_threadpool(compute)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    finally:
        slots.release()


build = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if build.is_dir():
    app.mount("/", StaticFiles(directory=build, html=True), name="frontend")
