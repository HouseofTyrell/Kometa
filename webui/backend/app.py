"""
Kometa Web UI - FastAPI Backend

A safe, read-only by default web interface for Kometa.
"""

import os
import json
import asyncio
import logging
import subprocess
import signal
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request

# Configure logging (temporarily DEBUG for troubleshooting)
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel
import aiosqlite

from backend.config_manager import ConfigManager
from backend.run_manager import RunManager
from backend.overlay_preview import OverlayPreviewManager
from backend.poster_fetcher import PosterFetcher
from backend.scheduler import scheduler


# Configuration from environment
CONFIG_DIR = Path(os.environ.get("KOMETA_CONFIG_DIR", "/config"))
# KOMETA_ROOT: Where the main Kometa source code lives (kometa.py, modules/, etc.)
# In Docker: mounted at /kometa; locally: relative to this file
KOMETA_ROOT = Path(os.environ.get("KOMETA_ROOT", "/kometa"))
UI_PORT = int(os.environ.get("KOMETA_UI_PORT", "8080"))
UI_HOST = os.environ.get("KOMETA_UI_HOST", "0.0.0.0")

# Safety: Apply mode kill switch (default: disabled)
APPLY_ENABLED = os.environ.get("KOMETA_UI_APPLY_ENABLED", "false").lower() == "true"

# Optional simple password protection
UI_PASSWORD = os.environ.get("KOMETA_UI_PASSWORD", "")

# Note: Legacy Jinja2 UI has been removed. Vue 3 SPA is the only supported mode.
UI_MODE = "vue"


# Initialize managers
config_manager: Optional[ConfigManager] = None
run_manager: Optional[RunManager] = None
overlay_manager: Optional[OverlayPreviewManager] = None
poster_fetcher: Optional[PosterFetcher] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    global config_manager, run_manager, overlay_manager, poster_fetcher

    # Ensure directories exist
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    (CONFIG_DIR / "backups").mkdir(exist_ok=True)
    (CONFIG_DIR / "logs" / "runs").mkdir(parents=True, exist_ok=True)

    # Initialize managers
    db_path = CONFIG_DIR / "webui.db"
    config_manager = ConfigManager(CONFIG_DIR)
    run_manager = RunManager(
        config_dir=CONFIG_DIR,
        kometa_root=KOMETA_ROOT,
        db_path=db_path,
        apply_enabled=APPLY_ENABLED
    )
    overlay_manager = OverlayPreviewManager(
        config_dir=CONFIG_DIR,
        kometa_root=KOMETA_ROOT
    )
    poster_fetcher = PosterFetcher(
        config_path=CONFIG_DIR / "config.yml"
    )

    await run_manager.init_db()

    # Initialize scheduler with run manager callback
    scheduler.set_callback(run_manager.start_run, asyncio.get_event_loop())

    print(f"Kometa Web UI starting on http://{UI_HOST}:{UI_PORT}")
    print(f"Config directory: {CONFIG_DIR}")
    print(f"Apply mode: {'ENABLED (use with caution!)' if APPLY_ENABLED else 'DISABLED (safe mode)'}")
    print(f"Vue frontend: {'Available' if vue_available else 'Not built - run npm run build in frontend-vue'}")

    yield

    # Cleanup
    scheduler.stop()
    await run_manager.close()


# Create FastAPI app
app = FastAPI(
    title="Kometa Web UI",
    description="Safe web interface for Kometa metadata automation",
    version="1.0.0",
    lifespan=lifespan
)

# Static files
vue_frontend_dir = Path(__file__).parent.parent / "frontend-vue" / "dist"

# Check if Vue build exists
vue_available = vue_frontend_dir.exists() and (vue_frontend_dir / "index.html").exists()

# Serve Vue 3 SPA assets if available
if vue_available and (vue_frontend_dir / "assets").exists():
    app.mount("/assets", StaticFiles(directory=vue_frontend_dir / "assets"), name="assets")

# Mount overlay images from defaults directory
overlay_images_dir = KOMETA_ROOT / "defaults" / "overlays" / "images"
if overlay_images_dir.exists():
    app.mount("/overlay-images", StaticFiles(directory=overlay_images_dir), name="overlay-images")


# Pydantic models
class ConfigSaveRequest(BaseModel):
    content: str


class RunRequest(BaseModel):
    dry_run: bool = True
    libraries: Optional[List[str]] = None
    collections: Optional[List[str]] = None
    run_type: Optional[str] = None  # collections, metadata, overlays, operations, playlists


class ApplyConfirmation(BaseModel):
    confirmation: str
    dry_run: bool = False
    libraries: Optional[List[str]] = None
    collections: Optional[List[str]] = None
    run_type: Optional[str] = None


# ============================================================================
# HTML Routes
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main UI page - serves the Vue 3 SPA."""
    if vue_available:
        return FileResponse(vue_frontend_dir / "index.html")
    else:
        # No frontend available
        return HTMLResponse(
            content="""
            <html>
            <head><title>Kometa Web UI</title></head>
            <body style="font-family: system-ui; padding: 2rem; max-width: 600px; margin: 0 auto;">
                <h1>Kometa Web UI</h1>
                <p>The Vue frontend is not built yet. Please run:</p>
                <pre style="background: #f5f5f5; padding: 1rem; border-radius: 4px;">
cd webui/frontend-vue
npm install
npm run build</pre>
                <p>Then restart the server.</p>
            </body>
            </html>
            """,
            status_code=503
        )


# ============================================================================
# Health Check
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "apply_enabled": APPLY_ENABLED,
        "config_dir": str(CONFIG_DIR),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/settings")
async def get_settings():
    """Get current Web UI settings."""
    return {
        "apply_enabled": APPLY_ENABLED,
        "password_required": bool(UI_PASSWORD),
        "ui_mode": UI_MODE,
        "vue_available": vue_available,
        "version": "1.0.0"
    }


class SettingsUpdateRequest(BaseModel):
    apply_enabled: Optional[bool] = None
    password: Optional[str] = None


@app.put("/api/settings")
async def update_settings(request: SettingsUpdateRequest):
    """Update Web UI settings.

    Note: apply_enabled can be toggled at runtime.
    Password changes require container/service restart with updated environment variable.
    """
    global APPLY_ENABLED

    updated = []

    if request.apply_enabled is not None:
        APPLY_ENABLED = request.apply_enabled
        # Also update the run manager's setting
        if run_manager:
            run_manager.apply_enabled = request.apply_enabled
        updated.append("apply_enabled")
        logger.info(f"Apply mode {'enabled' if APPLY_ENABLED else 'disabled'} via API")

    if request.password is not None:
        # Password changes cannot be applied at runtime for security reasons
        # They require setting the KOMETA_UI_PASSWORD environment variable
        return {
            "success": False,
            "message": "Password changes require restarting with updated KOMETA_UI_PASSWORD environment variable",
            "updated": updated
        }

    return {
        "success": True,
        "message": f"Settings updated: {', '.join(updated)}" if updated else "No changes",
        "updated": updated,
        "apply_enabled": APPLY_ENABLED
    }


@app.get("/api/libraries")
async def get_libraries():
    """Get list of libraries from config."""
    try:
        result = config_manager.load_config()
        parsed = result.get("parsed", {})
        libraries = []

        if parsed and "libraries" in parsed:
            for name, lib_config in parsed["libraries"].items():
                lib_type = "unknown"
                has_overlays = False
                # Try to determine library type from config
                if lib_config:
                    if "collection_files" in lib_config:
                        lib_type = "collection"
                    if "overlay_files" in lib_config:
                        has_overlays = True
                        if lib_type == "unknown":
                            lib_type = "overlay"
                        else:
                            lib_type = "both"
                libraries.append({
                    "name": name,
                    "type": lib_type,
                    "has_overlays": has_overlays
                })

        return {"libraries": libraries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Configuration Endpoints
# ============================================================================

@app.get("/api/config")
async def get_config():
    """Load the current config.yml."""
    try:
        config_path = CONFIG_DIR / "config.yml"
        if not config_path.exists():
            return {
                "exists": False,
                "content": "",
                "path": str(config_path),
                "message": "No config.yml found. You can create one or import an existing configuration."
            }

        result = config_manager.load_config()
        return {
            "exists": True,
            "content": result["content"],
            "path": str(config_path),
            "parsed": result.get("parsed"),
            "validation": result.get("validation")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config")
async def save_config(request: ConfigSaveRequest):
    """Save config.yml with automatic backup."""
    try:
        result = config_manager.save_config(request.content)
        return {
            "success": True,
            "backup_path": result.get("backup_path"),
            "validation": result.get("validation")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/config/validate")
async def validate_config(request: ConfigSaveRequest):
    """Validate YAML without saving."""
    try:
        result = config_manager.validate_yaml(request.content)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/config/backups")
async def list_backups():
    """List available config backups."""
    try:
        backups = config_manager.list_backups()
        # Normalize field names for frontend compatibility
        normalized = [
            {
                "filename": b.get("name", b.get("filename", "")),
                "created": b.get("created", ""),
                "size": b.get("size", 0),
            }
            for b in backups
        ]
        return {"backups": normalized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config/backup")
async def create_backup():
    """Create a manual backup of the current config."""
    try:
        config_path = CONFIG_DIR / "config.yml"
        if not config_path.exists():
            raise HTTPException(status_code=404, detail="No config.yml to backup")

        # Use the config manager's backup method
        backup_path = config_manager._create_backup()
        if backup_path is None:
            # Content is identical to most recent backup
            backups = config_manager.list_backups()
            if backups:
                return {
                    "success": True,
                    "filename": backups[0].get("name", ""),
                    "message": "Config unchanged from most recent backup"
                }
            raise HTTPException(status_code=500, detail="Failed to create backup")

        return {
            "success": True,
            "filename": backup_path.name
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config/restore/{backup_name}")
async def restore_backup(backup_name: str):
    """Restore config from a backup."""
    try:
        result = config_manager.restore_backup(backup_name)
        return {"success": True, "restored_from": backup_name}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Backup not found: {backup_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/config/backups/{backup_name}")
async def delete_backup(backup_name: str):
    """Delete a specific config backup."""
    try:
        config_manager.delete_backup(backup_name)
        return {"success": True, "deleted": backup_name}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Backup not found: {backup_name}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Run Endpoints
# ============================================================================

@app.get("/api/run/plan")
async def get_run_plan():
    """Generate a run plan preview based on current config."""
    try:
        plan = config_manager.generate_run_plan()
        plan["apply_enabled"] = APPLY_ENABLED
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/run")
async def start_run(request: RunRequest):
    """Start a Kometa run (dry-run by default)."""
    # Enforce dry-run if apply mode is disabled
    if not APPLY_ENABLED and not request.dry_run:
        raise HTTPException(
            status_code=403,
            detail="Apply mode is disabled. Set KOMETA_UI_APPLY_ENABLED=true to enable."
        )

    # For non-dry-run, require explicit confirmation via the /api/run/apply endpoint
    if not request.dry_run:
        raise HTTPException(
            status_code=400,
            detail="For apply mode, use POST /api/run/apply with confirmation."
        )

    try:
        run_info = await run_manager.start_run(
            dry_run=True,
            libraries=request.libraries,
            collections=request.collections,
            run_type=request.run_type
        )
        return run_info
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/run/apply")
async def start_apply_run(request: ApplyConfirmation):
    """Start a Kometa run in APPLY mode (requires confirmation)."""
    # Check kill switch
    if not APPLY_ENABLED:
        raise HTTPException(
            status_code=403,
            detail="Apply mode is disabled by KOMETA_UI_APPLY_ENABLED=false"
        )

    # Require exact confirmation text
    if request.confirmation != "APPLY CHANGES":
        raise HTTPException(
            status_code=400,
            detail="Invalid confirmation. Type exactly: APPLY CHANGES"
        )

    try:
        run_info = await run_manager.start_run(
            dry_run=False,
            libraries=request.libraries,
            collections=request.collections,
            run_type=request.run_type
        )
        return run_info
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/run/status")
async def get_run_status():
    """Get current run status."""
    status = await run_manager.get_status()
    return status


@app.post("/api/run/stop")
async def stop_run():
    """Stop the current run."""
    try:
        await run_manager.stop_run()
        return {"success": True, "message": "Run stopped"}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/runs")
async def list_runs(limit: int = 50, offset: int = 0):
    """List run history."""
    runs = await run_manager.list_runs(limit=limit, offset=offset)
    return {"runs": runs}


@app.get("/api/runs/{run_id}")
async def get_run(run_id: str):
    """Get details for a specific run."""
    run = await run_manager.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@app.get("/api/logs/{run_id}")
async def get_run_logs(run_id: str, tail: int = 1000):
    """Get logs for a specific run."""
    try:
        logs = await run_manager.get_logs(run_id, tail=tail)
        return {"run_id": run_id, "logs": logs}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Logs not found")


@app.get("/api/runs/{run_id}/diff")
async def get_run_diff(run_id: str):
    """
    Parse dry run logs and return structured diff data.

    Returns a summary of what changes would have been made during a dry run,
    organized by operation type and collection.
    """
    import re
    from collections import defaultdict

    # Get run info first
    run = await run_manager.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    if not run.get("dry_run"):
        return {
            "run_id": run_id,
            "is_dry_run": False,
            "message": "This run was not a dry run - no diff preview available",
            "summary": None,
            "operations": []
        }

    try:
        logs = await run_manager.get_logs(run_id, tail=None)  # Get full logs
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Logs not found")

    # Parse dry run operations from logs
    operations = []
    operation_counts = defaultdict(int)
    collections_affected = defaultdict(lambda: {"added": 0, "removed": 0, "updated": 0})

    # Patterns for parsing dry run logs
    dry_run_pattern = re.compile(
        r'\[DRY RUN\] Would (\w+)(?:\s+on\s+[\'"]([^"\']+)[\'"])?:\s*(.*)',
        re.IGNORECASE
    )

    collection_add_pattern = re.compile(
        r'(?:Would add|Adding)\s+(\d+)\s+(?:items?|movies?|shows?)\s+to\s+[\'"]([^"\']+)[\'"]',
        re.IGNORECASE
    )

    collection_remove_pattern = re.compile(
        r'(?:Would remove|Removing)\s+(\d+)\s+(?:items?|movies?|shows?)\s+from\s+[\'"]([^"\']+)[\'"]',
        re.IGNORECASE
    )

    summary_section = False
    summary_data = {}

    for line in logs:
        # Check for dry run operations
        match = dry_run_pattern.search(line)
        if match:
            operation = match.group(1).lower()
            target = match.group(2) or "Unknown"
            details = match.group(3).strip()

            operations.append({
                "operation": operation,
                "target": target,
                "details": details
            })
            operation_counts[operation] += 1

            # Categorize by collection impact
            if "playlist_add" in operation or "add_item" in operation:
                collections_affected[target]["added"] += 1
            elif "playlist_remove" in operation or "remove_item" in operation:
                collections_affected[target]["removed"] += 1
            elif "edit" in operation or "upload" in operation:
                collections_affected[target]["updated"] += 1
            continue

        # Check for collection add patterns
        add_match = collection_add_pattern.search(line)
        if add_match:
            count = int(add_match.group(1))
            collection = add_match.group(2)
            collections_affected[collection]["added"] += count
            operation_counts["collection_add"] += count
            continue

        # Check for collection remove patterns
        remove_match = collection_remove_pattern.search(line)
        if remove_match:
            count = int(remove_match.group(1))
            collection = remove_match.group(2)
            collections_affected[collection]["removed"] += count
            operation_counts["collection_remove"] += count
            continue

        # Parse summary section
        if "DRY RUN SUMMARY" in line.upper():
            summary_section = True
            continue

        if summary_section:
            if "Total operations" in line:
                total_match = re.search(r'(\d+)', line)
                if total_match:
                    summary_data["total_operations"] = int(total_match.group(1))
            elif ":" in line and "-" in line:
                # Parse operation count lines like "  - edit_metadata: 12"
                op_match = re.match(r'\s*-?\s*(\w+):\s*(\d+)', line)
                if op_match:
                    op_name = op_match.group(1)
                    op_count = int(op_match.group(2))
                    if "by_operation" not in summary_data:
                        summary_data["by_operation"] = {}
                    summary_data["by_operation"][op_name] = op_count

    # Build collection summary
    collection_summary = []
    for name, changes in collections_affected.items():
        if any(changes.values()):
            collection_summary.append({
                "name": name,
                "items_added": changes["added"],
                "items_removed": changes["removed"],
                "items_updated": changes["updated"]
            })

    # Sort by total impact
    collection_summary.sort(
        key=lambda x: x["items_added"] + x["items_removed"] + x["items_updated"],
        reverse=True
    )

    return {
        "run_id": run_id,
        "is_dry_run": True,
        "summary": {
            "total_operations": summary_data.get("total_operations", len(operations)),
            "operations_by_type": dict(operation_counts),
            "collections_affected": len(collection_summary),
            "total_added": sum(c["items_added"] for c in collection_summary),
            "total_removed": sum(c["items_removed"] for c in collection_summary),
            "total_updated": sum(c["items_updated"] for c in collection_summary),
        },
        "collections": collection_summary[:50],  # Limit to top 50
        "operations": operations[:100],  # Limit to first 100 operations
    }


@app.delete("/api/runs/{run_id}")
async def delete_run(run_id: str):
    """Delete a run from history and its associated log file."""
    try:
        await run_manager.delete_run(run_id)
        return {"success": True, "deleted": run_id}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WebSocket for Live Logs
# ============================================================================

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket endpoint for streaming live logs."""
    await websocket.accept()
    logger.info("WebSocket logs client connected")

    try:
        # Subscribe to log updates
        async for log_line in run_manager.stream_logs():
            try:
                await websocket.send_json({"type": "log", "data": log_line})
            except WebSocketDisconnect:
                logger.info("WebSocket logs client disconnected during send")
                break
    except WebSocketDisconnect:
        logger.info("WebSocket logs client disconnected")
    except Exception as e:
        logger.error("WebSocket logs error: %s", e)
        try:
            await websocket.send_json({"type": "error", "data": str(e)})
        except Exception:
            pass  # Client likely disconnected


@app.websocket("/ws/status")
async def websocket_status(websocket: WebSocket):
    """WebSocket endpoint for run status updates with heartbeat."""
    await websocket.accept()
    logger.info("WebSocket status client connected")

    heartbeat_interval = 30  # Send heartbeat every 30 seconds
    status_interval = 2  # Send status every 2 seconds
    last_heartbeat = asyncio.get_event_loop().time()

    try:
        while True:
            current_time = asyncio.get_event_loop().time()

            # Send heartbeat if needed
            if current_time - last_heartbeat >= heartbeat_interval:
                try:
                    await websocket.send_json({"type": "heartbeat", "timestamp": datetime.utcnow().isoformat()})
                    last_heartbeat = current_time
                except WebSocketDisconnect:
                    logger.info("WebSocket status client disconnected during heartbeat")
                    break

            # Send status update
            try:
                status = await run_manager.get_status()
                status["type"] = "status"
                await websocket.send_json(status)
            except WebSocketDisconnect:
                logger.info("WebSocket status client disconnected during status send")
                break

            await asyncio.sleep(status_interval)
    except WebSocketDisconnect:
        logger.info("WebSocket status client disconnected")
    except Exception as e:
        logger.error("WebSocket status error: %s", e)


# ============================================================================
# Overlay Preview Endpoints
# ============================================================================

class OverlayPreviewRequest(BaseModel):
    overlays: List[Dict[str, Any]]
    canvas_type: str = "portrait"  # portrait, landscape, square
    poster_source: Optional[str] = None  # plex, tmdb, or None for sample
    rating_key: Optional[str] = None  # Plex rating key
    tmdb_id: Optional[str] = None  # TMDb ID
    media_type: str = "movie"  # movie, tv


@app.get("/api/overlays")
async def get_available_overlays():
    """Get list of available overlay configurations."""
    try:
        overlays = overlay_manager.get_available_overlays()
        # Add debug info about paths being searched
        overlays["_debug"] = {
            "defaults_dir": str(overlay_manager.defaults_dir),
            "defaults_exists": overlay_manager.defaults_dir.exists(),
            "config_dir": str(overlay_manager.config_dir),
            "config_overlays_dir": str(overlay_manager.config_dir / "overlays"),
            "config_overlays_exists": (overlay_manager.config_dir / "overlays").exists(),
        }
        return overlays
    except Exception as e:
        logger.error("Failed to get overlays: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/overlays/images")
async def get_overlay_images():
    """Get list of available overlay images."""
    try:
        images = overlay_manager.get_overlay_images_list()
        return {"images": images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/overlays/parse")
async def parse_overlay_file(file_path: str, template_vars: Optional[str] = None):
    """
    Parse an overlay YAML file.

    Args:
        file_path: Path to the overlay file
        template_vars: JSON-encoded template variables (optional)
    """
    try:
        # Parse template variables if provided
        user_template_vars = None
        if template_vars:
            import json
            try:
                user_template_vars = json.loads(template_vars)
            except json.JSONDecodeError:
                pass

        result = overlay_manager.parse_overlay_file(file_path, user_template_vars)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/overlays/preview")
async def generate_overlay_preview(request: OverlayPreviewRequest):
    """Generate a preview image with overlays applied."""
    try:
        # Fetch poster and metadata if a source is specified
        sample_poster = None
        media_metadata = None

        if request.poster_source == "plex" and request.rating_key:
            # Fetch poster image
            poster_data = poster_fetcher.fetch_poster_image(
                rating_key=request.rating_key
            )
            if poster_data:
                # Save to temp file for overlay manager
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                    f.write(poster_data)
                    sample_poster = f.name

            # Fetch metadata for text variable substitution
            media_metadata = poster_fetcher.get_plex_item_metadata(request.rating_key)

        elif request.poster_source == "tmdb" and request.tmdb_id:
            poster_data = poster_fetcher.fetch_poster_image(
                tmdb_id=request.tmdb_id,
                media_type=request.media_type
            )
            if poster_data:
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                    f.write(poster_data)
                    sample_poster = f.name

        result = overlay_manager.generate_preview(
            overlays=request.overlays,
            canvas_type=request.canvas_type,
            sample_poster=sample_poster,
            media_metadata=media_metadata
        )

        # Clean up temp file
        if sample_poster:
            import os
            try:
                os.unlink(sample_poster)
            except OSError:
                pass  # File already deleted or inaccessible

        return result
    except Exception as e:
        logger.error("Overlay preview error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


class SimpleOverlayPreviewRequest(BaseModel):
    """Simplified preview request that takes overlay name and media ID."""
    overlay_name: str  # Name of the overlay file (e.g., "rating", "resolution")
    media_id: str  # Plex rating key
    poster_source: str = "tmdb"  # "tmdb" for clean poster, "plex" for current poster
    library: Optional[str] = None  # Library name to get overlay config from (optional)
    settings: Optional[Dict[str, Any]] = None  # Optional overlay settings (overrides config.yml)
    config_content: Optional[str] = None  # Optional YAML config content (uses this instead of disk config.yml)


def get_overlay_template_variables_from_config(
    overlay_name: str,
    library: Optional[str] = None,
    config_content: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extract template_variables for a specific overlay from the user's config.

    Searches the config's library overlay_files sections for matching overlay definitions
    and returns any template_variables defined for that overlay.

    Args:
        overlay_name: Name of the overlay (e.g., "ratings", "resolution")
        library: Optional library name to search in (if None, searches all libraries)
        config_content: Optional YAML string content. If provided, uses this instead of reading from disk.

    Returns:
        Dictionary of template_variables, empty dict if none found
    """
    try:
        import ruamel.yaml
        yaml = ruamel.yaml.YAML()
        yaml.preserve_quotes = True

        if config_content:
            # Parse config from provided content
            from io import StringIO
            config = yaml.load(StringIO(config_content))
        else:
            # Read config from disk
            config_path = CONFIG_DIR / "config.yml"
            if not config_path.exists():
                return {}
            with open(config_path, encoding="utf-8") as f:
                config = yaml.load(f)

        if not config or "libraries" not in config:
            return {}

        # Collect all template_variables for the overlay from all libraries
        all_template_vars: Dict[str, Any] = {}

        for lib_name, lib_config in config.get("libraries", {}).items():
            # Skip if library filter is specified and doesn't match
            if library and lib_name != library:
                continue

            if not isinstance(lib_config, dict):
                continue

            overlay_files = lib_config.get("overlay_files", [])
            if not overlay_files:
                continue

            for overlay_entry in overlay_files:
                if not isinstance(overlay_entry, dict):
                    continue

                # Check if this entry matches our overlay
                entry_name = overlay_entry.get("default") or overlay_entry.get("file", "")

                # Handle both "default: ratings" and "file: config/overlays/custom.yml"
                if isinstance(entry_name, str):
                    # Strip path and extension for comparison
                    entry_base_name = entry_name.replace(".yml", "").replace(".yaml", "")
                    if "/" in entry_base_name:
                        entry_base_name = entry_base_name.split("/")[-1]

                    # Check if names match (case-insensitive)
                    if entry_base_name.lower() == overlay_name.lower():
                        template_vars = overlay_entry.get("template_variables", {})
                        if template_vars:
                            # Merge template_variables (later entries override earlier ones)
                            all_template_vars.update(template_vars)

        return all_template_vars

    except Exception as e:
        logger.warning("Failed to extract overlay template_variables from config: %s", e)
        return {}


@app.post("/api/overlays/preview/simple")
async def generate_simple_overlay_preview(request: SimpleOverlayPreviewRequest):
    """
    Generate a preview using just the overlay name and media ID.

    This is a simplified endpoint that:
    1. Looks up the overlay file by name
    2. Parses it to get overlay configurations
    3. Fetches the poster from Plex
    4. Generates the preview
    """
    try:
        # Find the overlay file by name
        available = overlay_manager.get_available_overlays()
        overlay_file = None

        # Check default overlays
        for ov in available.get("default", []):
            if ov["name"] == request.overlay_name or ov["name"] == request.overlay_name.replace("custom/", ""):
                overlay_file = ov
                break

        # Check custom overlays
        if not overlay_file:
            for ov in available.get("custom", []):
                if ov["name"] == request.overlay_name or f"custom/{ov['name']}" == request.overlay_name:
                    overlay_file = ov
                    break

        if not overlay_file:
            raise HTTPException(
                status_code=404,
                detail=f"Overlay '{request.overlay_name}' not found. Available: {[o['name'] for o in available.get('default', [])]}"
            )

        # Get template_variables from config for this overlay
        # Uses provided config_content if available, otherwise reads from disk
        config_template_vars = get_overlay_template_variables_from_config(
            request.overlay_name,
            library=request.library,
            config_content=request.config_content
        )

        # Merge with any settings provided in the request (request settings override config)
        template_vars = {**config_template_vars}
        if request.settings:
            template_vars.update(request.settings)

        logger.debug("Using template_variables for %s: %s", request.overlay_name, template_vars)

        # Parse the overlay file with template_variables
        parsed = overlay_manager.parse_overlay_file(
            overlay_file["path"],
            template_variables=template_vars if template_vars else None
        )
        overlays = parsed.get("overlays", [])

        if not overlays:
            raise HTTPException(
                status_code=400,
                detail=f"No overlays found in '{request.overlay_name}'"
            )

        # Reload config to get latest Plex credentials
        poster_fetcher.reload_config()

        # Fetch poster and metadata
        sample_poster = None
        media_metadata = None
        poster_data = None

        if poster_fetcher.has_plex:
            # Always get metadata from Plex (needed for text variables)
            media_metadata = poster_fetcher.get_plex_item_metadata(request.media_id)

            # Determine poster source
            if request.poster_source == "tmdb" and poster_fetcher.has_tmdb:
                # Use TMDb clean poster if available
                tmdb_id = media_metadata.get("tmdb_id") if media_metadata else None
                media_type = media_metadata.get("media_type", "movie") if media_metadata else "movie"

                if tmdb_id:
                    poster_data = poster_fetcher.fetch_poster_image(
                        tmdb_id=tmdb_id,
                        media_type=media_type
                    )
                    logger.debug("Fetched TMDb poster for tmdb_id=%s", tmdb_id)

                # Fallback to Plex if TMDb poster not available
                if not poster_data:
                    logger.debug("TMDb poster not available, falling back to Plex")
                    poster_data = poster_fetcher.fetch_poster_image(rating_key=request.media_id)
            else:
                # Use Plex poster (current poster with any existing overlays)
                poster_data = poster_fetcher.fetch_poster_image(rating_key=request.media_id)

            if poster_data:
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                    f.write(poster_data)
                    sample_poster = f.name

        # Generate preview with all overlays from the file
        result = overlay_manager.generate_preview(
            overlays=overlays,
            canvas_type="portrait",
            sample_poster=sample_poster,
            media_metadata=media_metadata,
            queues=parsed.get("queue_positions", {})
        )

        # Clean up temp file
        if sample_poster:
            import os
            try:
                os.unlink(sample_poster)
            except OSError:
                pass

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Simple overlay preview error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


class ConfigOverlayPreviewRequest(BaseModel):
    """Preview request that uses overlays from the config."""
    media_id: str  # Plex rating key
    library: str  # Library name to get overlay config from
    poster_source: str = "tmdb"  # "tmdb" for clean poster, "plex" for current poster
    config_content: Optional[str] = None  # Optional YAML config content (uses this instead of disk config.yml)


def get_library_overlays_from_config(
    library: str,
    config_content: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Extract overlay_files configuration for a library from the config.

    Returns a list of overlay file entries with their template_variables.
    """
    try:
        import ruamel.yaml
        yaml = ruamel.yaml.YAML()
        yaml.preserve_quotes = True

        if config_content:
            from io import StringIO
            config = yaml.load(StringIO(config_content))
        else:
            config_path = CONFIG_DIR / "config.yml"
            if not config_path.exists():
                return []
            with open(config_path, encoding="utf-8") as f:
                config = yaml.load(f)

        if not config or "libraries" not in config:
            return []

        lib_config = config.get("libraries", {}).get(library)
        if not lib_config or not isinstance(lib_config, dict):
            return []

        overlay_files = lib_config.get("overlay_files", [])
        if not overlay_files:
            return []

        return list(overlay_files)

    except Exception as e:
        logger.warning("Failed to extract overlay_files from config: %s", e)
        return []


@app.post("/api/overlays/preview/from-config")
async def generate_config_overlay_preview(request: ConfigOverlayPreviewRequest):
    """
    Generate a preview using overlays configured for a library in config.yml.

    This reads the overlay_files section for the specified library and
    renders all configured overlays on the media item's poster.
    """
    try:
        # Get overlay_files from config for this library
        overlay_entries = get_library_overlays_from_config(
            request.library,
            config_content=request.config_content
        )

        if not overlay_entries:
            raise HTTPException(
                status_code=400,
                detail=f"No overlay_files configured for library '{request.library}'"
            )

        logger.info("Config overlay preview: Found %d overlay entries for library '%s'", len(overlay_entries), request.library)
        for i, entry in enumerate(overlay_entries):
            logger.info("  Entry %d: %s", i, entry)

        # Get available overlays to match against
        available = overlay_manager.get_available_overlays()
        all_available = {ov["name"]: ov for ov in available.get("default", [])}
        for ov in available.get("custom", []):
            all_available[f"custom/{ov['name']}"] = ov

        logger.info("Available overlays: %d default, %d custom",
                    len(available.get("default", [])), len(available.get("custom", [])))

        # Collect all overlays to render
        all_overlays = []
        all_queues = {}

        for entry in overlay_entries:
            if not isinstance(entry, dict):
                logger.warning("Skipping non-dict entry: %s", entry)
                continue

            # Get the overlay name (default: or file:)
            overlay_name = entry.get("default") or entry.get("file", "")
            if not overlay_name:
                logger.warning("Entry has no default or file key: %s", entry)
                continue

            # Get template_variables for this overlay
            template_vars = entry.get("template_variables", {})
            logger.info("Processing overlay '%s' with template_vars: %s", overlay_name, template_vars)

            # Find the overlay file
            overlay_file = None
            # Try exact match first
            if overlay_name in all_available:
                overlay_file = all_available[overlay_name]
                logger.info("  Found exact match: %s", overlay_file.get("path", "unknown"))
            else:
                # Try matching by base name
                base_name = overlay_name.replace(".yml", "").replace(".yaml", "")
                if "/" in base_name:
                    base_name = base_name.split("/")[-1]
                for name, ov in all_available.items():
                    if ov["name"] == base_name or ov["name"].endswith(f"/{base_name}"):
                        overlay_file = ov
                        logger.info("  Found by base name '%s': %s", base_name, ov.get("path", "unknown"))
                        break

            if not overlay_file:
                logger.warning("Overlay '%s' not found in available overlays", overlay_name)
                continue

            # Parse the overlay file with template_variables
            try:
                parsed = overlay_manager.parse_overlay_file(
                    overlay_file["path"],
                    template_variables=dict(template_vars) if template_vars else None
                )
                overlays_from_file = parsed.get("overlays", [])
                logger.info("  Parsed %d overlays from '%s'", len(overlays_from_file), overlay_name)
                for ov in overlays_from_file:
                    logger.info("    - %s (type=%s, image_url=%s)",
                                ov.get("name", "?"), ov.get("type", "?"), ov.get("image_url", "none"))
                all_overlays.extend(overlays_from_file)

                # Merge queue positions
                file_queues = parsed.get("queue_positions", {})
                if file_queues:
                    logger.info("  Queue positions: %s", list(file_queues.keys()))
                for queue_name, queue_items in file_queues.items():
                    if queue_name not in all_queues:
                        all_queues[queue_name] = []
                    all_queues[queue_name].extend(queue_items)

            except Exception as e:
                logger.warning("Failed to parse overlay '%s': %s", overlay_name, e, exc_info=True)
                continue

        if not all_overlays:
            raise HTTPException(
                status_code=400,
                detail=f"No valid overlays found in library '{request.library}' config"
            )

        # For preview, filter to show only one overlay per group
        # For rating groups, prefer "Fresh" variants as they represent normal ratings
        # For other groups, use highest weight
        groups_seen = {}
        filtered_overlays = []

        def get_overlay_name(ov_dict):
            """Get the best available name for an overlay."""
            return ov_dict.get("_original_name") or ov_dict.get("display_name") or ov_dict.get("name", "")

        for ov in all_overlays:
            group = ov.get("group")
            if group:
                if group not in groups_seen:
                    groups_seen[group] = ov
                else:
                    # Get names using fallback chain
                    current_name = get_overlay_name(ov)
                    existing_name = get_overlay_name(groups_seen[group])

                    # For rating groups, prefer Fresh > Rotten > Top
                    is_rating_group = group.startswith("rating") and group.endswith("_group")
                    if is_rating_group:
                        current_is_fresh = "Fresh" in str(current_name)
                        existing_is_fresh = "Fresh" in str(existing_name)

                        # Fresh is preferred for normal preview - always replace non-Fresh with Fresh
                        if current_is_fresh and not existing_is_fresh:
                            groups_seen[group] = ov
                        # Don't replace Fresh with anything else
                    else:
                        # For non-rating groups, use weight
                        if ov.get("weight", 0) > groups_seen[group].get("weight", 0):
                            groups_seen[group] = ov
            else:
                filtered_overlays.append(ov)

        # Add one overlay per group
        filtered_overlays.extend(groups_seen.values())

        logger.info("After group filtering: %d overlays (from %d total) for library '%s'",
                    len(filtered_overlays), len(all_overlays), request.library)
        for ov in filtered_overlays:
            logger.info("  - %s (group=%s, default=%s)",
                        ov.get("_original_name", ov.get("name", "?")),
                        ov.get("group", "none"),
                        ov.get("default", "none"))

        all_overlays = filtered_overlays

        # Reload config to get latest Plex credentials
        poster_fetcher.reload_config()

        # Fetch poster and metadata
        sample_poster = None
        media_metadata = None
        poster_data = None

        if poster_fetcher.has_plex:
            media_metadata = poster_fetcher.get_plex_item_metadata(request.media_id)

            if request.poster_source == "tmdb" and poster_fetcher.has_tmdb:
                tmdb_id = media_metadata.get("tmdb_id") if media_metadata else None
                media_type = media_metadata.get("media_type", "movie") if media_metadata else "movie"

                if tmdb_id:
                    poster_data = poster_fetcher.fetch_poster_image(
                        tmdb_id=tmdb_id,
                        media_type=media_type
                    )

                if not poster_data:
                    poster_data = poster_fetcher.fetch_poster_image(rating_key=request.media_id)
            else:
                poster_data = poster_fetcher.fetch_poster_image(rating_key=request.media_id)

            if poster_data:
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                    f.write(poster_data)
                    sample_poster = f.name

        # Generate preview
        result = overlay_manager.generate_preview(
            overlays=all_overlays,
            canvas_type="portrait",
            sample_poster=sample_poster,
            media_metadata=media_metadata,
            queues=all_queues
        )

        # Clean up temp file
        if sample_poster:
            import os
            try:
                os.unlink(sample_poster)
            except OSError:
                pass

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Config overlay preview error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/overlays/debug-expand")
async def debug_expand_overlay(
    overlay_name: str = "ratings",
    template_vars: Optional[str] = None
):
    """Debug endpoint to test template expansion."""
    try:
        import json

        # Parse template_vars if provided
        user_vars = {}
        if template_vars:
            user_vars = json.loads(template_vars)

        # Find the overlay file
        available = overlay_manager.get_available_overlays()
        overlay_file = None
        for ov in available.get("default", []):
            if ov["name"] == overlay_name:
                overlay_file = ov
                break

        if not overlay_file:
            return {"error": f"Overlay '{overlay_name}' not found"}

        # Parse with template expansion
        parsed = overlay_manager.parse_overlay_file(
            overlay_file["path"],
            template_variables=user_vars
        )

        # Return detailed info
        return {
            "overlay_name": overlay_name,
            "template_vars": user_vars,
            "overlay_count": len(parsed.get("overlays", [])),
            "overlays": [
                {
                    "name": ov.get("name"),
                    "display_name": ov.get("display_name"),
                    "type": ov.get("type"),
                    "default": ov.get("default"),
                    "group": ov.get("group"),
                    "horizontal_offset": ov.get("horizontal_offset"),
                    "horizontal_align": ov.get("horizontal_align"),
                    "vertical_offset": ov.get("vertical_offset"),
                    "vertical_align": ov.get("vertical_align"),
                }
                for ov in parsed.get("overlays", [])
            ]
        }
    except Exception as e:
        logger.error("Debug expand error: %s", e, exc_info=True)
        return {"error": str(e)}


@app.get("/api/overlays/defaults")
async def get_default_overlays():
    """Get list of default overlay configurations with details."""
    try:
        overlays = overlay_manager.get_available_overlays()
        detailed = []

        for overlay_file in overlays.get("default", []):
            try:
                parsed = overlay_manager.parse_overlay_file(overlay_file["path"])
                detailed.append({
                    "name": overlay_file["name"],
                    "path": overlay_file["path"],
                    "overlay_count": len(parsed.get("overlays", [])),
                    "queue_count": len(parsed.get("queues", [])),
                    "overlays": parsed.get("overlays", [])[:5]  # First 5 for preview
                })
            except Exception:
                detailed.append({
                    "name": overlay_file["name"],
                    "path": overlay_file["path"],
                    "error": "Failed to parse"
                })

        return {"defaults": detailed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Media Search & Poster Endpoints (for overlay preview)
# ============================================================================

@app.get("/api/media/status")
async def get_media_sources_status():
    """Get status of available media sources (Plex, TMDb)."""
    try:
        # Reload config to get latest status
        poster_fetcher.reload_config()
        status = poster_fetcher.get_status()
        # Add debug info about config path
        status["_debug"] = {
            "config_path": str(poster_fetcher.config_path),
            "config_exists": poster_fetcher.config_path.exists(),
        }
        return status
    except Exception as e:
        logger.error("Failed to get media status: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/media/libraries")
async def get_plex_libraries():
    """Get list of Plex libraries."""
    try:
        libraries = poster_fetcher.get_plex_libraries()
        return {"libraries": libraries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/media/search")
async def search_media(
    query: str,
    source: str = "plex",  # plex or tmdb
    media_type: str = "movie",  # movie or tv
    library: Optional[str] = None,
    limit: int = 20
):
    """Search for media items in Plex or TMDb."""
    try:
        # Reload config to pick up any changes
        poster_fetcher.reload_config()

        # Include debug info about configuration status
        debug_info = {
            "config_path": str(poster_fetcher.config_path),
            "config_exists": poster_fetcher.config_path.exists(),
            "plex_configured": poster_fetcher.has_plex,
            "tmdb_configured": poster_fetcher.has_tmdb,
        }

        if source == "plex":
            if not poster_fetcher.has_plex:
                return {
                    "results": [],
                    "source": source,
                    "query": query,
                    "error": "Plex not configured. Add plex.url and plex.token to config.yml.",
                    "_debug": debug_info
                }
            results = poster_fetcher.search_plex(query, library=library, limit=limit)
        elif source == "tmdb":
            if not poster_fetcher.has_tmdb:
                return {
                    "results": [],
                    "source": source,
                    "query": query,
                    "error": "TMDb not configured. Add tmdb.apikey to config.yml.",
                    "_debug": debug_info
                }
            results = poster_fetcher.search_tmdb(query, media_type=media_type, limit=limit)
        else:
            raise HTTPException(status_code=400, detail=f"Invalid source: {source}")

        return {"results": results, "source": source, "query": query, "_debug": debug_info}
    except Exception as e:
        logger.error("Media search error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/media/recent")
async def get_recent_media(library_key: str, limit: int = 20):
    """Get recently added media from a Plex library."""
    try:
        items = poster_fetcher.get_recent_items(library_key, limit=limit)
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/media/poster")
async def get_poster(
    rating_key: Optional[str] = None,
    tmdb_id: Optional[str] = None,
    media_type: str = "movie",
    width: Optional[int] = None,
    height: Optional[int] = None
):
    """Fetch a poster image and return as base64 data URI."""
    try:
        resize = None
        if width and height:
            resize = (width, height)

        result = poster_fetcher.fetch_poster_base64(
            rating_key=rating_key,
            tmdb_id=tmdb_id,
            media_type=media_type,
            resize=resize
        )

        if not result:
            raise HTTPException(status_code=404, detail="Poster not found")

        return {"poster": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/media/{media_id}")
async def get_media_item(media_id: str):
    """Get detailed information about a specific media item.

    Args:
        media_id: The Plex rating key for the media item
    """
    try:
        # Use the poster_fetcher's Plex item metadata method
        metadata = poster_fetcher.get_plex_item_metadata(media_id)

        if not metadata:
            raise HTTPException(status_code=404, detail=f"Media item not found: {media_id}")

        return metadata
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Connection Test Endpoints
# ============================================================================

class PlexTestRequest(BaseModel):
    url: str
    token: str


class TmdbTestRequest(BaseModel):
    apikey: str


class ArrTestRequest(BaseModel):
    url: str
    token: str


class TautulliTestRequest(BaseModel):
    url: str
    apikey: str


class ApiKeyTestRequest(BaseModel):
    apikey: str


class TraktTestRequest(BaseModel):
    client_id: str
    client_secret: Optional[str] = None


class MalTestRequest(BaseModel):
    client_id: str


class AnidbTestRequest(BaseModel):
    client: str
    version: str


class GithubTestRequest(BaseModel):
    token: str


class GotifyTestRequest(BaseModel):
    url: str
    token: str


class NtfyTestRequest(BaseModel):
    url: str
    topic: str


@app.post("/api/test/plex")
async def test_plex_connection(request: PlexTestRequest):
    """Test Plex server connection."""
    import httpx

    try:
        url = request.url.rstrip('/')
        headers = {
            "X-Plex-Token": request.token,
            "Accept": "application/json"
        }

        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            response = await client.get(f"{url}/", headers=headers)

            if response.status_code == 200:
                data = response.json()
                server_name = data.get("MediaContainer", {}).get("friendlyName", "Plex Server")
                return {"success": True, "server_name": server_name}
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid token"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except httpx.ConnectError:
        return {"success": False, "error": "Connection refused - check URL"}
    except httpx.TimeoutException:
        return {"success": False, "error": "Connection timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/tmdb")
async def test_tmdb_connection(request: TmdbTestRequest):
    """Test TMDb API key."""
    import httpx

    try:
        url = f"https://api.themoviedb.org/3/configuration?api_key={request.apikey}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)

            if response.status_code == 200:
                return {"success": True, "message": "API key is valid"}
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid API key"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/radarr")
async def test_radarr_connection(request: ArrTestRequest):
    """Test Radarr connection."""
    import httpx

    try:
        url = request.url.rstrip('/')
        headers = {"X-Api-Key": request.token}

        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            response = await client.get(f"{url}/api/v3/system/status", headers=headers)

            if response.status_code == 200:
                data = response.json()
                version = data.get("version", "unknown")
                return {"success": True, "message": f"Connected to Radarr v{version}"}
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid API token"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except httpx.ConnectError:
        return {"success": False, "error": "Connection refused - check URL"}
    except httpx.TimeoutException:
        return {"success": False, "error": "Connection timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/sonarr")
async def test_sonarr_connection(request: ArrTestRequest):
    """Test Sonarr connection."""
    import httpx

    try:
        url = request.url.rstrip('/')
        headers = {"X-Api-Key": request.token}

        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            response = await client.get(f"{url}/api/v3/system/status", headers=headers)

            if response.status_code == 200:
                data = response.json()
                version = data.get("version", "unknown")
                return {"success": True, "message": f"Connected to Sonarr v{version}"}
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid API token"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except httpx.ConnectError:
        return {"success": False, "error": "Connection refused - check URL"}
    except httpx.TimeoutException:
        return {"success": False, "error": "Connection timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/tautulli")
async def test_tautulli_connection(request: TautulliTestRequest):
    """Test Tautulli connection."""
    import httpx

    try:
        url = request.url.rstrip('/')
        params = {"apikey": request.apikey, "cmd": "get_server_info"}

        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            response = await client.get(f"{url}/api/v2", params=params)

            if response.status_code == 200:
                data = response.json()
                if data.get("response", {}).get("result") == "success":
                    return {"success": True, "message": "Connected to Tautulli"}
                else:
                    return {"success": False, "error": "Invalid API key"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except httpx.ConnectError:
        return {"success": False, "error": "Connection refused - check URL"}
    except httpx.TimeoutException:
        return {"success": False, "error": "Connection timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/mdblist")
async def test_mdblist_connection(request: ApiKeyTestRequest):
    """Test MDBList API key."""
    import httpx

    try:
        url = f"https://mdblist.com/api/user/?apikey={request.apikey}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)

            if response.status_code == 200:
                data = response.json()
                if "error" not in data:
                    return {"success": True, "message": "API key is valid"}
                else:
                    return {"success": False, "error": data.get("error", "Unknown error")}
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid API key"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/omdb")
async def test_omdb_connection(request: ApiKeyTestRequest):
    """Test OMDb API key."""
    import httpx

    try:
        url = f"https://www.omdbapi.com/?apikey={request.apikey}&t=test"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)

            if response.status_code == 200:
                data = response.json()
                if data.get("Response") == "True" or "Error" not in data or "Invalid API key" not in data.get("Error", ""):
                    return {"success": True, "message": "API key is valid"}
                elif "Invalid API key" in data.get("Error", ""):
                    return {"success": False, "error": "Invalid API key"}
                else:
                    return {"success": True, "message": "API key is valid"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/trakt")
async def test_trakt_connection(request: TraktTestRequest):
    """Test Trakt API credentials."""
    import httpx

    try:
        headers = {
            "Content-Type": "application/json",
            "trakt-api-version": "2",
            "trakt-api-key": request.client_id
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://api.trakt.tv/lists/trending", headers=headers)

            if response.status_code == 200:
                return {"success": True, "message": "Client ID is valid"}
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid Client ID"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/mal")
async def test_mal_connection(request: MalTestRequest):
    """Test MyAnimeList API credentials."""
    import httpx

    try:
        headers = {"X-MAL-CLIENT-ID": request.client_id}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.myanimelist.net/v2/anime/ranking?ranking_type=all&limit=1",
                headers=headers
            )

            if response.status_code == 200:
                return {"success": True, "message": "Client ID is valid"}
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid Client ID"}
            elif response.status_code == 403:
                return {"success": False, "error": "Client ID forbidden - check app settings"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/anidb")
async def test_anidb_connection(request: AnidbTestRequest):
    """Test AniDB API credentials."""
    # AniDB API is rate-limited and doesn't have a simple test endpoint
    # Just validate that the client name is lowercase and version is numeric
    if not request.client.islower():
        return {"success": False, "error": "Client name must be lowercase"}

    if not request.version.isdigit():
        return {"success": False, "error": "Version must be a number"}

    return {"success": True, "message": "Credentials format is valid (AniDB connection will be tested during run)"}


@app.post("/api/test/github")
async def test_github_connection(request: GithubTestRequest):
    """Test GitHub personal access token."""
    import httpx

    try:
        headers = {"Authorization": f"token {request.token}"}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://api.github.com/user", headers=headers)

            if response.status_code == 200:
                data = response.json()
                username = data.get("login", "unknown")
                return {"success": True, "message": f"Authenticated as {username}"}
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid token"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/notifiarr")
async def test_notifiarr_connection(request: ApiKeyTestRequest):
    """Test Notifiarr API key."""
    import httpx

    try:
        headers = {"x-api-key": request.apikey}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://notifiarr.com/api/v1/user/validate", headers=headers)

            if response.status_code == 200:
                return {"success": True, "message": "API key is valid"}
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid API key"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/gotify")
async def test_gotify_connection(request: GotifyTestRequest):
    """Test Gotify connection."""
    import httpx

    try:
        url = request.url.rstrip('/')
        headers = {"X-Gotify-Key": request.token}

        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            response = await client.get(f"{url}/version", headers=headers)

            if response.status_code == 200:
                data = response.json()
                version = data.get("version", "unknown")
                return {"success": True, "message": f"Connected to Gotify v{version}"}
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid token"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except httpx.ConnectError:
        return {"success": False, "error": "Connection refused - check URL"}
    except httpx.TimeoutException:
        return {"success": False, "error": "Connection timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/ntfy")
async def test_ntfy_connection(request: NtfyTestRequest):
    """Test ntfy connection by sending a test notification."""
    import httpx

    try:
        url = request.url.rstrip('/')

        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            # Just check if the ntfy server is reachable
            response = await client.get(f"{url}/{request.topic}/json?poll=1")

            if response.status_code in [200, 304]:
                return {"success": True, "message": f"Connected to ntfy topic '{request.topic}'"}
            elif response.status_code == 404:
                return {"success": False, "error": "Topic not found"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except httpx.ConnectError:
        return {"success": False, "error": "Connection refused - check URL"}
    except httpx.TimeoutException:
        return {"success": False, "error": "Connection timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# NEW API ENDPOINTS - Stubs for Phase 7-10 Features
# See docs/API_INTEGRATION.md for full implementation details
# ============================================================================

# Request/Response Models for new endpoints
class WebhookTestRequest(BaseModel):
    """Request model for testing webhooks."""
    url: str
    event: str = "test"
    service: str = "custom"  # discord, slack, teams, custom


class MetadataBrowseResponse(BaseModel):
    """Response model for metadata browsing."""
    items: List[Dict[str, Any]]
    total: int
    page: int
    total_pages: int


class MetadataEditRequest(BaseModel):
    """Request model for editing item metadata."""
    title: Optional[str] = None
    sort_title: Optional[str] = None
    year: Optional[int] = None
    content_rating: Optional[str] = None
    summary: Optional[str] = None
    genres: Optional[str] = None
    labels: Optional[str] = None


class CollectionSaveRequest(BaseModel):
    """Request model for saving a collection."""
    library: str
    name: str
    builders: List[Dict[str, Any]]
    filters: Optional[List[Dict[str, Any]]] = None
    settings: Optional[Dict[str, Any]] = None


class ScheduleSettingsRequest(BaseModel):
    """Request model for schedule settings."""
    run_order: Optional[List[str]] = None
    global_schedule: Optional[str] = None
    library_schedules: Optional[Dict[str, Dict[str, Any]]] = None


class SchedulerConfigRequest(BaseModel):
    """Request model for automated scheduler configuration."""
    enabled: bool = False
    schedule: Optional[str] = None
    dry_run_only: bool = True


class MapperSettingsRequest(BaseModel):
    """Request model for data mapper settings."""
    genre_mapper: Optional[Dict[str, str]] = None
    content_rating_mapper: Optional[Dict[str, str]] = None
    studio_mapper: Optional[Dict[str, str]] = None


class NotificationSettingsRequest(BaseModel):
    """Request model for notification settings."""
    enabled_events: List[str]
    webhooks: Optional[Dict[str, str]] = None


class OperationsConfigRequest(BaseModel):
    """Request model for advanced operations configuration."""
    enabled: List[str]
    settings: Optional[Dict[str, Any]] = None


# --- Webhook Testing ---

@app.post("/api/webhooks/test")
async def test_webhook(request: WebhookTestRequest):
    """
    Test a webhook by sending a test notification.

    Automatically detects service type from URL (Discord, Slack, Teams)
    and formats the payload appropriately.
    """
    import httpx

    try:
        # Detect service from URL if not specified
        service = request.service
        if "discord.com" in request.url:
            service = "discord"
        elif "slack.com" in request.url or "hooks.slack" in request.url:
            service = "slack"
        elif "office.com" in request.url:
            service = "teams"

        # Build payload based on service
        if service == "discord":
            payload = {
                "content": None,
                "embeds": [{
                    "title": f"Kometa Test - {request.event}",
                    "description": "This is a test notification from Kometa Web UI",
                    "color": 15105570  # Kometa gold
                }]
            }
        elif service == "slack":
            payload = {
                "text": f"Kometa Test - {request.event}",
                "blocks": [{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Kometa Test Notification*\nThis is a test notification from Kometa Web UI"
                    }
                }]
            }
        elif service == "teams":
            payload = {
                "@type": "MessageCard",
                "themeColor": "e5a00d",
                "title": f"Kometa Test - {request.event}",
                "text": "This is a test notification from Kometa Web UI"
            }
        else:
            payload = {
                "event": request.event,
                "message": "Kometa test notification",
                "timestamp": datetime.now().isoformat()
            }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(request.url, json=payload)

            if response.status_code in [200, 204]:
                return {"success": True, "message": f"Test notification sent successfully ({service})"}
            else:
                return {"success": False, "error": f"Webhook returned HTTP {response.status_code}"}

    except httpx.ConnectError:
        return {"success": False, "error": "Connection refused - check URL"}
    except httpx.TimeoutException:
        return {"success": False, "error": "Connection timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# --- Metadata Browser ---

@app.get("/api/metadata/browse/{library}")
async def browse_metadata(
    library: str,
    page: int = 1,
    per_page: int = 24,
    search: str = "",
    type: str = "all",
    sort: str = "title"
):
    """
    Browse media items in a library for metadata viewing.

    Uses the PosterFetcher to query the Plex API for library contents.
    Note: This is read-only - metadata editing should be done in Plex directly.
    """
    if not poster_fetcher or not poster_fetcher.has_plex:
        return {
            "items": [],
            "total": 0,
            "page": page,
            "total_pages": 0,
            "error": "Plex not configured. Add Plex credentials to config.yml."
        }

    try:
        # If search is provided, use search functionality
        if search:
            items = poster_fetcher.search_plex(search, library=library, limit=per_page)
            return {
                "items": items,
                "total": len(items),
                "page": 1,
                "total_pages": 1,
                "search": search
            }

        # Otherwise, get recent items from the library
        # Find the library key from the library name
        libraries = poster_fetcher.get_plex_libraries()
        library_key = None
        for lib in libraries:
            if lib["title"].lower() == library.lower() or lib["key"] == library:
                library_key = lib["key"]
                break

        if not library_key:
            return {
                "items": [],
                "total": 0,
                "page": page,
                "total_pages": 0,
                "error": f"Library '{library}' not found"
            }

        items = poster_fetcher.get_recent_items(library_key, limit=per_page)
        return {
            "items": items,
            "total": len(items),
            "page": page,
            "total_pages": 1
        }

    except Exception as e:
        logger.error("Failed to browse metadata: %s", e)
        return {
            "items": [],
            "total": 0,
            "page": page,
            "total_pages": 0,
            "error": str(e)
        }


@app.get("/api/metadata/item/{item_id}")
async def get_metadata_item(item_id: str):
    """
    Get full metadata for a specific Plex item.

    Uses PosterFetcher to retrieve detailed metadata from Plex.
    """
    if not poster_fetcher or not poster_fetcher.has_plex:
        raise HTTPException(
            status_code=503,
            detail="Plex not configured. Add Plex credentials to config.yml."
        )

    try:
        metadata = poster_fetcher.get_plex_item_metadata(item_id)
        if not metadata:
            raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

        # Add poster URL
        poster_url = poster_fetcher.get_plex_poster_url(item_id)
        if poster_url:
            metadata["poster_url"] = poster_url

        return {
            "id": item_id,
            "metadata": metadata
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get metadata item: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/metadata/item/{item_id}")
async def update_metadata_item(item_id: str, request: MetadataEditRequest):
    """
    Update metadata for a specific item.

    Note: Direct Plex metadata editing via API is limited. This endpoint
    returns guidance on how to edit metadata properly through Kometa's
    metadata files or Plex directly.
    """
    return {
        "success": False,
        "message": "Direct metadata editing is not supported via the Web UI for safety reasons. "
                   "To edit metadata, use Kometa metadata files (metadata.yml) or edit directly in Plex. "
                   "See: https://kometa.wiki/en/latest/files/metadata/"
    }


@app.post("/api/metadata/generate-yaml")
async def generate_metadata_yaml(items: List[Dict[str, Any]]):
    """
    Generate Kometa metadata YAML from provided items.

    Accepts a list of items with title, year, and optional metadata fields.
    Returns valid Kometa metadata.yml format.
    """
    from io import StringIO
    from ruamel.yaml import YAML

    if not items:
        return {"yaml": "metadata:\n  # Add items to generate metadata YAML\n"}

    yaml = YAML()
    yaml.default_flow_style = False
    yaml.preserve_quotes = True

    metadata_dict = {"metadata": {}}

    for item in items:
        title = item.get("title", "Unknown Title")
        year = item.get("year")

        # Create the item key (title or title (year))
        item_key = f"{title} ({year})" if year else title

        # Build the metadata entry
        entry = {}

        # Add optional fields if provided
        if item.get("sort_title"):
            entry["sort_title"] = item["sort_title"]
        if item.get("content_rating"):
            entry["content_rating"] = item["content_rating"]
        if item.get("critic_rating"):
            entry["critic_rating"] = item["critic_rating"]
        if item.get("audience_rating"):
            entry["audience_rating"] = item["audience_rating"]
        if item.get("originally_available"):
            entry["originally_available"] = item["originally_available"]
        if item.get("studio"):
            entry["studio"] = item["studio"]
        if item.get("tagline"):
            entry["tagline"] = item["tagline"]
        if item.get("summary"):
            entry["summary"] = item["summary"]
        if item.get("genres"):
            entry["genre"] = item["genres"]
        if item.get("labels"):
            entry["label"] = item["labels"]

        # If no optional fields, add a comment placeholder
        if not entry:
            entry["# Add metadata fields"] = None

        metadata_dict["metadata"][item_key] = entry

    # Convert to YAML string
    stream = StringIO()
    yaml.dump(metadata_dict, stream)
    yaml_output = stream.getvalue()

    return {"yaml": yaml_output}


# --- Collection Builder ---

@app.get("/api/collections/{library}")
async def get_collections(library: str):
    """Get existing collections for a library from collection files."""
    collection_files = config_manager.get_collection_files()

    # Filter by library and load collections
    collections = []
    for cf in collection_files:
        if cf["library"] == library:
            file_data = config_manager.load_collection_file(cf["path"])
            if file_data.get("exists") and file_data.get("collections"):
                for coll in file_data["collections"]:
                    coll["source_file"] = cf["path"]
                    collections.append(coll)

    return {"collections": collections, "files": collection_files}


@app.post("/api/collections/save")
async def save_collection(request: CollectionSaveRequest):
    """Save a collection definition to a YAML file."""
    # Determine file path - use library name as default
    file_path = f"config/{request.library.lower().replace(' ', '_')}_collections.yml"

    # Build collection config
    collection_config = {}

    # Add builders
    for builder in request.builders:
        source = builder.get("source", "unknown")
        config = builder.get("config", {})
        if config:
            collection_config[source] = config
        else:
            collection_config[source] = builder.get("value", True)

    # Add filters if present
    if request.filters:
        filters = {}
        for f in request.filters:
            field = f.get("field", "")
            operator = f.get("operator", "")
            value = f.get("value", "")
            filter_key = f"{field}.{operator}" if operator else field
            filters[filter_key] = value
        if filters:
            collection_config["filters"] = filters

    # Add settings if present
    if request.settings:
        collection_config.update(request.settings)

    # Load existing collections from file
    file_data = config_manager.load_collection_file(file_path)
    existing = file_data.get("collections", []) if file_data.get("exists") else []

    # Update or add the collection
    found = False
    for i, coll in enumerate(existing):
        if coll["name"] == request.name:
            existing[i] = {"name": request.name, "config": collection_config}
            found = True
            break

    if not found:
        existing.append({"name": request.name, "config": collection_config})

    # Save to file
    success = config_manager.save_collection_file(file_path, existing)

    if success:
        return {"success": True, "message": f"Collection '{request.name}' saved to {file_path}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save collection")


@app.post("/api/collections/preview")
async def preview_collection(request: CollectionSaveRequest):
    """
    Preview the YAML that would be generated for a collection.
    """
    # Generate YAML preview
    yaml_output = f"collections:\n  {request.name}:\n"
    for builder in request.builders:
        source = builder.get("source", "unknown")
        yaml_output += f"    {source}:\n"
        for key, value in builder.get("config", {}).items():
            yaml_output += f"      {key}: {value}\n"

    return {"yaml": yaml_output}


class CollectionFileSaveRequest(BaseModel):
    """Request model for saving a collection/overlay file with raw YAML."""
    filename: str
    content: str  # Raw YAML content
    file_type: str = "collection"  # collection or overlay


@app.post("/api/collections/file/save")
async def save_collection_file(request: CollectionFileSaveRequest):
    """
    Save a collection or overlay file with raw YAML content.

    This is used by the Collection & Overlay Editor to save files.
    """
    import re

    # Validate filename
    if not request.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    # Sanitize filename - only allow alphanumeric, underscore, hyphen, period
    safe_filename = re.sub(r'[^a-zA-Z0-9_\-.]', '_', request.filename)
    if not safe_filename.endswith(('.yml', '.yaml')):
        safe_filename += '.yml'

    # Determine the directory based on file type
    if request.file_type == "overlay":
        file_dir = CONFIG_DIR / "overlays"
    else:
        file_dir = CONFIG_DIR

    file_dir.mkdir(parents=True, exist_ok=True)
    file_path = file_dir / safe_filename

    # Validate YAML content
    try:
        from io import StringIO
        from ruamel.yaml import YAML
        yaml = YAML()
        yaml.load(StringIO(request.content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {str(e)}")

    # Create backup if file exists
    if file_path.exists():
        backup_dir = CONFIG_DIR / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = backup_dir / f"{safe_filename}.{timestamp}"
        try:
            backup_path.write_text(file_path.read_text(encoding="utf-8"), encoding="utf-8")
        except Exception:
            pass  # Non-critical if backup fails

    # Save the file
    try:
        file_path.write_text(request.content, encoding="utf-8")
        return {
            "success": True,
            "message": f"File saved: {safe_filename}",
            "path": str(file_path)
        }
    except Exception as e:
        logger.error("Failed to save collection file: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


@app.get("/api/collections/file/{filename}")
async def load_collection_file(filename: str):
    """
    Load a collection or overlay file by filename.
    """
    import re

    # Sanitize filename
    safe_filename = re.sub(r'[^a-zA-Z0-9_\-.]', '_', filename)

    # Try to find the file in config dir or overlays dir
    possible_paths = [
        CONFIG_DIR / safe_filename,
        CONFIG_DIR / "overlays" / safe_filename,
    ]

    for file_path in possible_paths:
        if file_path.exists():
            try:
                content = file_path.read_text(encoding="utf-8")
                return {
                    "exists": True,
                    "filename": safe_filename,
                    "path": str(file_path),
                    "content": content
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")

    return {
        "exists": False,
        "filename": safe_filename,
        "content": ""
    }


@app.get("/api/collections/files")
async def list_collection_files():
    """
    List all collection and overlay files in the config directory.
    """
    files = []

    # List collection files in config dir
    for pattern in ["*.yml", "*.yaml"]:
        for file_path in CONFIG_DIR.glob(pattern):
            if file_path.name != "config.yml" and file_path.is_file():
                try:
                    stat = file_path.stat()
                    files.append({
                        "name": file_path.name,
                        "path": str(file_path),
                        "type": "overlay" if "overlay" in file_path.name.lower() else "collection",
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except Exception:
                    pass

    # List files in overlays subdirectory
    overlay_dir = CONFIG_DIR / "overlays"
    if overlay_dir.exists():
        for pattern in ["*.yml", "*.yaml"]:
            for file_path in overlay_dir.glob(pattern):
                if file_path.is_file():
                    try:
                        stat = file_path.stat()
                        files.append({
                            "name": file_path.name,
                            "path": str(file_path),
                            "type": "overlay",
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
                    except Exception:
                        pass

    # Sort by modification time, newest first
    files.sort(key=lambda f: f.get("modified", ""), reverse=True)

    return {"files": files}


@app.get("/api/builders/sources")
async def get_builder_sources():
    """
    Get available builder sources and their configuration options.
    """
    # Return available sources
    sources = {
        "tmdb_popular": {"name": "TMDb Popular", "category": "charts", "fields": ["limit"]},
        "tmdb_trending": {"name": "TMDb Trending", "category": "charts", "fields": ["limit", "time_window"]},
        "trakt_list": {"name": "Trakt List", "category": "lists", "fields": ["list_url"]},
        "imdb_list": {"name": "IMDb List", "category": "lists", "fields": ["list_id"]},
        "plex_search": {"name": "Plex Search", "category": "plex", "fields": ["any"]},
    }
    return {"sources": sources}


# --- Playlist Builder ---

@app.get("/api/playlists")
async def get_playlists():
    """Get existing playlists from playlist files."""
    from io import StringIO

    playlist_files = config_manager.get_playlist_files()
    playlists = []

    # Parse each playlist file to extract playlist definitions
    for pf in playlist_files:
        file_path = pf.get("file_path")
        if file_path and Path(file_path).exists():
            try:
                content = Path(file_path).read_text(encoding="utf-8")
                yaml = config_manager.yaml
                parsed = yaml.load(StringIO(content))

                if parsed and isinstance(parsed, dict):
                    # Look for playlists key
                    playlist_defs = parsed.get("playlists", parsed)
                    if isinstance(playlist_defs, dict):
                        for playlist_name, playlist_config in playlist_defs.items():
                            if isinstance(playlist_config, dict):
                                playlists.append({
                                    "name": playlist_name,
                                    "source_file": pf.get("path"),
                                    "library": pf.get("library"),
                                    "libraries": playlist_config.get("libraries"),
                                    "sync_to_users": playlist_config.get("sync_to_users"),
                                    "builders": _extract_builders(playlist_config),
                                })
            except Exception as e:
                logger.warning(f"Failed to parse playlist file {file_path}: {e}")

    return {"playlists": playlists, "files": playlist_files}


def _extract_builders(playlist_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract builder configurations from a playlist config."""
    builders = []
    # Known builder keys
    builder_keys = [
        "plex_all", "plex_search", "plex_pilots", "plex_watchlist",
        "tmdb_popular", "tmdb_trending", "tmdb_discover", "tmdb_list",
        "trakt_list", "trakt_watchlist", "trakt_trending", "trakt_popular",
        "imdb_list", "imdb_chart", "letterboxd_list", "mdblist_list",
        "tautulli_popular", "tautulli_watched", "anilist_popular",
    ]

    for key in builder_keys:
        if key in playlist_config:
            config = playlist_config[key]
            builders.append({
                "source": key,
                "config": config if isinstance(config, dict) else {}
            })

    return builders


@app.post("/api/playlists/save")
async def save_playlist(request: Dict[str, Any]):
    """Save a playlist definition to a YAML file."""
    from io import StringIO

    name = request.get("name", "New Playlist")
    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="Playlist name is required")

    # Sanitize filename
    safe_name = "".join(c if c.isalnum() or c in "._- " else "_" for c in name)
    file_path = CONFIG_DIR / f"playlists-{safe_name.lower().replace(' ', '-')}.yml"

    # Build playlist config from request
    playlist_config = {}
    if request.get("libraries"):
        playlist_config["libraries"] = request["libraries"]
    if request.get("sync_to_users"):
        playlist_config["sync_to_users"] = request["sync_to_users"]

    # Add builders
    if request.get("builders"):
        for builder in request["builders"]:
            source = builder.get("source", "plex_all")
            config = builder.get("config", {})
            # If config is empty dict, use True for simple builders
            playlist_config[source] = config if config else True

    # Wrap in playlists key with the playlist name
    full_config = {"playlists": {name: playlist_config}}

    # Write to file
    try:
        yaml = config_manager.yaml
        stream = StringIO()
        yaml.dump(full_config, stream)
        file_path.write_text(stream.getvalue(), encoding="utf-8")

        return {
            "success": True,
            "message": f"Playlist '{name}' saved to {file_path.name}",
            "path": str(file_path),
            "config": playlist_config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save playlist: {e}")


# --- Settings Endpoints ---

@app.get("/api/settings/schedule")
async def get_schedule_settings():
    """Get scheduling configuration from config.yml."""
    return config_manager.get_schedule_settings()


@app.post("/api/settings/schedule")
async def save_schedule_settings(request: ScheduleSettingsRequest):
    """Save scheduling configuration to config.yml."""
    success = config_manager.save_schedule_settings(
        run_order=request.run_order,
        global_schedule=request.global_schedule,
        library_schedules=request.library_schedules
    )
    if success:
        return {"success": True, "message": "Schedule settings saved"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save schedule settings")


# --- Automated Scheduler Endpoints ---

@app.get("/api/scheduler/status")
async def get_scheduler_status():
    """Get current status of the automated scheduler."""
    return scheduler.get_status()


@app.post("/api/scheduler/configure")
async def configure_scheduler(request: SchedulerConfigRequest):
    """Configure the automated scheduler.

    When enabled, the scheduler will automatically trigger Kometa runs
    based on the configured schedule expression.
    """
    try:
        status = scheduler.configure(
            enabled=request.enabled,
            schedule_expression=request.schedule,
            dry_run_only=request.dry_run_only
        )
        return {
            "success": True,
            "message": "Scheduler configured" if request.enabled else "Scheduler disabled",
            "status": status
        }
    except Exception as e:
        logger.error("Failed to configure scheduler: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to configure scheduler: {str(e)}")


@app.post("/api/scheduler/stop")
async def stop_scheduler():
    """Stop the automated scheduler."""
    scheduler.stop()
    return {"success": True, "message": "Scheduler stopped", "status": scheduler.get_status()}


@app.get("/api/settings/mappers")
async def get_mapper_settings():
    """Get data mapper settings from config.yml."""
    return config_manager.get_mapper_settings()


@app.post("/api/settings/mappers")
async def save_mapper_settings(request: MapperSettingsRequest):
    """Save data mapper settings to config.yml."""
    success = config_manager.save_mapper_settings(
        genre_mapper=request.genre_mapper,
        content_rating_mapper=request.content_rating_mapper,
        studio_mapper=request.studio_mapper
    )
    if success:
        return {"success": True, "message": "Mapper settings saved"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save mapper settings")


@app.get("/api/settings/notifications")
async def get_notification_settings():
    """Get notification/webhook settings from config.yml."""
    settings = config_manager.get_webhook_settings()
    # Extract enabled events from webhooks (events with non-empty URLs)
    webhooks = settings.get("webhooks", {}) or {}
    enabled_events = [event for event, url in webhooks.items() if url]
    return {
        "enabled_events": enabled_events,
        "webhooks": webhooks
    }


@app.post("/api/settings/notifications")
async def save_notification_settings(request: NotificationSettingsRequest):
    """Save notification settings to config.yml."""
    # Build webhooks dict from enabled events and URLs
    webhooks = request.webhooks or {}
    success = config_manager.save_webhook_settings(webhooks=webhooks)
    if success:
        return {"success": True, "message": "Notification settings saved"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save notification settings")


# --- Operations Config ---

@app.get("/api/operations/config")
async def get_operations_config():
    """Get advanced operations configuration from config.yml."""
    return config_manager.get_operations_settings()


@app.post("/api/operations/config")
async def save_operations_config(request: OperationsConfigRequest, library: str = "Movies"):
    """Save advanced operations configuration to config.yml."""
    # Build operations dict from enabled operations
    operations = {}
    for op in request.enabled:
        # Map operation IDs to config keys
        op_key = op.replace("op-", "").replace("-", "_")
        operations[op_key] = True

    # Merge with any additional settings
    if request.settings:
        operations.update(request.settings)

    success = config_manager.save_operations_settings(library, operations)
    if success:
        return {"success": True, "message": "Operations settings saved"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save operations settings")


# ============================================================================
# Catch-all Route for Vue SPA (MUST be last)
# ============================================================================

@app.get("/{full_path:path}")
async def serve_spa(request: Request, full_path: str):
    """
    Serve Vue SPA for all non-API routes (client-side routing support).

    IMPORTANT: This route MUST be defined last, after all API routes,
    otherwise it will capture API requests before they reach their handlers.
    """
    # Skip API and WebSocket routes - they should have been handled above
    if full_path.startswith(("api/", "ws/", "static/", "assets/", "overlay-images/")):
        raise HTTPException(status_code=404, detail="Not found")

    if UI_MODE == "vue" and vue_available:
        # Check if it's a static file
        file_path = vue_frontend_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        # Otherwise return index.html for client-side routing
        return FileResponse(vue_frontend_dir / "index.html")
    else:
        # Legacy mode or no frontend - 404 for unknown routes
        raise HTTPException(status_code=404, detail="Not found")


# ============================================================================
# Main entry point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=UI_HOST, port=UI_PORT)
