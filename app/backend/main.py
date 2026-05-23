"""
AETHER AI — Backend API
FastAPI server that wraps the ComfyUI image generation pipeline.
"""

import json, os, sys, time, shutil, random
from pathlib import Path
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent.parent  # AetherAI/
WORKFLOW_DIR = PROJECT_DIR / "comfyui_workflows"
OUTPUT_DIR = PROJECT_DIR / "app" / "backend" / "generated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
COMFY_OUTPUT_DIR = Path(r"C:\Users\aratz\Documents\comfy\ComfyUI") / "output"

COMFY_API = "http://127.0.0.1:8188"

STYLES = {
    "white_bg": {
        "workflow": "klein_white_background.json",
        "label": "White Background",
        "desc": "Pure white e-commerce studio, soft lighting, clean shadows",
    },
    "studio": {
        "workflow": "klein_studio_lighting.json",
        "label": "Studio Lighting",
        "desc": "Warm diffused studio lighting, gradient backdrop",
    },
    "lifestyle": {
        "workflow": "klein_lifestyle.json",
        "label": "Lifestyle",
        "desc": "Natural use setting, window lighting, bokeh background",
    },
    "outdoor": {
        "workflow": "klein_outdoor_natural.json",
        "label": "Outdoor Natural",
        "desc": "Golden hour sunlight, nature backdrop, warm tones",
    },
    "automotive": {
        "workflow": "klein_automotive.json",
        "label": "Automotive",
        "desc": "Dramatic dark studio, polished surfaces, high contrast",
    },
}

app = FastAPI(title="AETHER AI API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    description: str
    style: str = "white_bg"
    seed: int | None = None


class GenerateResponse(BaseModel):
    success: bool
    image_url: str
    style: str
    seed: int
    elapsed_s: float
    prompt_id: str | None = None


@app.get("/api/styles")
def get_styles():
    """List available photography styles with preview images."""
    return {
        name: {
            "label": info["label"],
            "desc": info["desc"],
            "workflow": info["workflow"],
        }
        for name, info in STYLES.items()
    }


@app.post("/api/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    """Generate a product image from a description."""
    if req.style not in STYLES:
        raise HTTPException(400, f"Invalid style. Choose from: {list(STYLES.keys())}")

    wf_path = WORKFLOW_DIR / STYLES[req.style]["workflow"]
    if not wf_path.exists():
        raise HTTPException(500, f"Workflow file missing: {wf_path}")

    import requests as http_req

    seed = req.seed if req.seed is not None else random.randint(1, 999999999)

    # Load and populate the workflow
    with open(wf_path) as f:
        wf = json.load(f)

    prompt_template = wf["2"]["inputs"]["text"]
    wf["2"]["inputs"]["text"] = prompt_template.format(desc=req.description)
    wf["7"]["inputs"]["seed"] = seed
    wf["7"]["inputs"]["steps"] = 6

    # Submit to ComfyUI
    start = time.time()
    try:
        resp = http_req.post(f"{COMFY_API}/prompt", json={"prompt": wf}, timeout=30)
        result = resp.json()
    except Exception as e:
        raise HTTPException(503, f"ComfyUI unreachable: {e}")

    if "prompt_id" not in result:
        raise HTTPException(500, f"ComfyUI error: {result}")

    prompt_id = result["prompt_id"]

    # Poll for completion
    for _ in range(200):
        time.sleep(3)
        try:
            hist = http_req.get(f"{COMFY_API}/history/{prompt_id}", timeout=10).json()
        except Exception:
            continue

        if hist.get(prompt_id):
            data = hist[prompt_id]
            for node_id, node_out in data.get("outputs", {}).items():
                for img in node_out.get("images", []):
                    src = COMFY_OUTPUT_DIR / img["filename"]
                    if src.exists():
                        dest = OUTPUT_DIR / img["filename"]
                        shutil.copy2(str(src), str(dest))
                        elapsed = time.time() - start
                        return GenerateResponse(
                            success=True,
                            image_url=f"/api/image/{img['filename']}",
                            style=req.style,
                            seed=seed,
                            elapsed_s=round(elapsed, 1),
                            prompt_id=prompt_id,
                        )
            break

        # Check if still queued
        try:
            q = http_req.get(f"{COMFY_API}/queue", timeout=5).json()
            if not q.get("queue_running") and not q.get("queue_pending"):
                break
        except Exception:
            pass

    raise HTTPException(504, "Generation timed out")


@app.get("/api/image/{filename}")
def serve_image(filename: str):
    """Serve a generated image."""
    path = OUTPUT_DIR / filename
    if not path.exists():
        raise HTTPException(404)
    return FileResponse(str(path), media_type="image/png")


@app.get("/api/history")
def get_history(limit: int = Query(20, ge=1, le=100)):
    """List recently generated images."""
    files = sorted(OUTPUT_DIR.iterdir(), key=os.path.getmtime, reverse=True)
    results = []
    for f in files[:limit]:
        results.append({
            "filename": f.name,
            "url": f"/api/image/{f.name}",
            "size_kb": round(f.stat().st_size / 1024, 1),
            "created": f.stat().st_mtime,
        })
    return {"images": results}


@app.get("/api/health")
def health():
    """Check ComfyUI connectivity."""
    import requests as http_req
    try:
        r = http_req.get(f"{COMFY_API}/queue", timeout=5)
        queue = r.json()
        running = len(queue.get("queue_running", []))
        pending = len(queue.get("queue_pending", []))
        return {"status": "ok", "comfyui_running": True, "queue_running": running, "queue_pending": pending}
    except Exception as e:
        return {"status": "ok", "comfyui_running": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    print(f"[AETHER] API starting on http://localhost:8111")
    print(f"[AETHER] ComfyUI: {COMFY_API}")
    print(f"[AETHER] Styles available: {list(STYLES.keys())}")
    uvicorn.run(app, host="127.0.0.1", port=8111)
