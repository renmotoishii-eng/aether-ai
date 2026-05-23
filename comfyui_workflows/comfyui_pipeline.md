# AETHER AI — ComfyUI Product Photography Pipeline

## Overview

This document explains how to install, configure, and use the 5 AETHER AI product photography workflows in ComfyUI. These workflows use **Flux.1 Dev FP8** as the primary model and produce studio-quality e-commerce product photography.

### Workflow Files

| File | Style | Use Case |
|------|-------|----------|
| `white_background.json` | Clean white bg (#FFFFFF) | Amazon / eBay / catalog listings |
| `studio_lighting.json` | Warm studio 45 lighting | Premium brand product pages |
| `lifestyle.json` | Natural use setting | Social media / marketing |
| `outdoor_natural.json` | Golden hour outdoor | Outdoor gear / summer products |
| `automotive.json` | Dark bg metallic studio | Car parts / automotive accessories |

---

## 1. Installation

### 1.1 Prerequisites

- ComfyUI installed (Windows, Linux, or via RunPod / Paperspace)
- At least 12 GB VRAM (Flux.1 Dev FP8 requires ~8-12 GB)
- ComfyUI Manager installed (recommended)

### 1.2 Install the Flux Model

Download Flux.1 Dev FP8 (the quantized version that fits consumer GPUs):

```
From HuggingFace:
  - Model: black-forest-labs/FLUX.1-dev
  - Quant: flux1-dev-fp8.safetensors (~6.9 GB)

Place the model file in:
  ComfyUI/models/checkpoints/flux1-dev-fp8.safetensors
```

Or install via ComfyUI Manager:
1. Open ComfyUI in browser
2. Click "Manager" -> "Model Manager"
3. Search for "flux1-dev-fp8"
4. Click Download

### 1.3 Install Custom Nodes (Required)

Install these nodes via ComfyUI Manager:
1. Click "Manager" -> "Install Custom Nodes"
2. Search and install each:

| Node | Purpose | Git URL |
|------|---------|---------|
| **ComfyUI-Manager** | Node management (already installed if Manager works) | https://github.com/ltdrdata/ComfyUI-Manager |
| **Efficient Nodes** | FluxGuidance support | Built-in (ComfyUI 0.2.0+) |
| **rgthree-comfy** | Optional: better UI grouping | https://github.com/rgthree/rgthree-comfy |

**Built-in nodes used** (no install needed in ComfyUI 0.2.0+):
- `CheckpointLoaderSimple`
- `CLIPTextEncode`
- `EmptyLatentImage`
- `ModelSamplingFlux`
- `FluxGuidance`
- `KSampler`
- `VAEDecode`
- `SaveImage`

All 5 workflows use only built-in ComfyUI nodes — no external custom node packs required for basic operation.

### 1.4 Add Workflows to ComfyUI

**Option A — Drag & Drop:**
1. Launch ComfyUI and open browser at `http://localhost:8188`
2. Drag a `.json` workflow file from Explorer into the ComfyUI canvas
3. Click "Load" when prompted

**Option B — Load from File Menu:**
1. Click "Load" (top menu bar)
2. Select the `.json` workflow file
3. Confirm load

**Option C — API Mode (Automation):**
Send via POST to `/prompt` endpoint (see Section 2 below).

---

## 2. API Endpoint Usage

ComfyUI exposes a REST API for headless / automated generation. Each workflow JSON is already in the correct **API format** — no conversion needed.

### 2.1 Endpoint

```
POST http://localhost:8188/prompt
```

### 2.2 Request Format

Send the workflow JSON as the payload:

```bash
curl -X POST http://localhost:8188/prompt \
  -H "Content-Type: application/json" \
  -d @white_background.json
```

### 2.3 Python Example

```python
import json
import requests

COMIFY_URL = "http://localhost:8188"

with open("comfyui_workflows/white_background.json", "r") as f:
    workflow = json.load(f)

response = requests.post(f"{COMIFY_URL}/prompt", json={"prompt": workflow})
data = response.json()
print(f"Prompt queued: {data.get('prompt_id')}")
```

### 2.4 Monitor Progress

```python
import requests

prompt_id = "your-prompt-id-here"
history = requests.get(f"{COMIFY_URL}/history/{prompt_id}").json()
status = history[prompt_id].get("status", {})
print(f"Status: {status}")
```

### 2.5 Retrieve Output Images

Images are saved to `ComfyUI/output/` by default. The filename prefix is set per workflow (e.g., `aether_white_bg_00001.png`).

---

## 3. Injecting Custom Prompts at Generation Time

To generate different products without modifying the workflow file, override the CLIPTextEncode node text at API call time.

### 3.1 Node Targeting

Each workflow uses consistent node IDs:

| Node ID | Class | Purpose |
|---------|-------|---------|
| `1` | CheckpointLoaderSimple | Loads flux1-dev-fp8 |
| `2` | CLIPTextEncode | **Positive prompt — OVERRIDE THIS** |
| `3` | CLIPTextEncode | Negative prompt |
| `4` | EmptyLatentImage | Image dimensions |
| `5` | ModelSamplingFlux | Flux noise schedule |
| `6` | FluxGuidance | Guidance scale |
| `7` | KSampler | Sampling parameters |
| `8` | VAEDecode | Decodes latent to pixels |
| `9` | SaveImage | Saves output |

### 3.2 Override Node Text in API Call

Replace the text input of node `"2"` with your product description:

```python
import json
import requests

with open("comfyui_workflows/studio_lighting.json", "r") as f:
    workflow = json.load(f)

# Inject custom product prompt
workflow["2"]["inputs"]["text"] = (
    "Professional studio product photography, "
    "a minimalist white ceramic vase on marble surface, "
    "soft diffused studio lighting from 45 degree angle, "
    "warm professional tones, gradient background #E8E8E8 to #FFFFFF, "
    "gentle reflections, soft shadows, commercial quality, 8K"
)

# Optionally change seed for variety
workflow["7"]["inputs"]["seed"] = 999999

response = requests.post(
    "http://localhost:8188/prompt",
    json={"prompt": workflow}
)
print(response.json())
```

### 3.3 Prompt Template System

For production use, create prompt templates per workflow:

```python
PRODUCT_TEMPLATES = {
    "white_bg": (
        "Professional e-commerce product photography, "
        "{product_description}, "
        "centered on pure white background #FFFFFF, "
        "soft studio lighting, crisp focus, subtle ground shadow, "
        "commercial product photography, 8K"
    ),
    "studio_lighting": (
        "Professional studio product photography, "
        "{product_description}, "
        "soft diffused lighting from 45 degree angle, "
        "warm tones, gradient background #E8E8E8 to #FFFFFF, "
        "gentle reflections, commercial quality, 8K"
    ),
    "lifestyle": (
        "Lifestyle product photography, "
        "{product_description} in natural use setting, "
        "warm natural lighting, shallow depth of field, "
        "blurred background bokeh, editorial style, 8K"
    ),
    "outdoor": (
        "Outdoor product photography, "
        "{product_description}, "
        "golden hour warm sunlight, soft diffused shadows, "
        "natural environment, nature backdrop, 8K"
    ),
    "automotive": (
        "Professional automotive product photography, "
        "{product_description}, "
        "dark background, dramatic studio lighting, "
        "metallic reflections, chrome highlights, "
        "commercial automotive photography, 8K"
    )
}

def generate_product(product_desc, style="white_bg", seed=None):
    with open(f"comfyui_workflows/{style}.json", "r") as f:
        workflow = json.load(f)
    
    prompt = PRODUCT_TEMPLATES[style].format(product_description=product_desc)
    workflow["2"]["inputs"]["text"] = prompt
    if seed is not None:
        workflow["7"]["inputs"]["seed"] = seed
    
    return requests.post(
        "http://localhost:8188/prompt",
        json={"prompt": workflow}
    ).json()
```

---

## 4. Workflow Parameter Reference

### Common Settings (All 5 Workflows)

| Parameter | Value | Notes |
|-----------|-------|-------|
| Model | flux1-dev-fp8.safetensors | FP8 quantized Flux.1 Dev |
| Width | 1024 | Square product format |
| Height | 1024 | Square product format |
| Steps | 28 | Standard for Flux quality |
| Sampler | euler | Good quality/speed balance |
| Scheduler | simple | Standard Flux scheduler |
| CFG | 3.5 | Classifier-free guidance scale |
| Flux Guidance | 3.5 | Flux-specific guidance |
| Denoise | 1.0 | Full generation (not img2img) |
| Batch Size | 1 | Single image per run |

### Per-Workflow Highlights

| Workflow | Seed | Prefix | Key Prompt Focus |
|----------|------|--------|------------------|
| white_bg | 123456789 | aether_white_bg | Pure white bg, ground shadow, no gradient |
| studio | 234567890 | aether_studio | 45 lighting, warm tones, E8E8E8-FFFFFF gradient bg |
| lifestyle | 345678901 | aether_lifestyle | Use setting, bokeh, warm natural light |
| outdoor | 456789012 | aether_outdoor | Golden hour, diffused shadows, nature |
| automotive | 567890123 | aether_automotive | Dark bg, metallic reflections, rim light |

---

## 5. Troubleshooting

### Model Not Found
```
Error: Checkpoint 'flux1-dev-fp8.safetensors' not found
```
**Fix:** Download the model to `ComfyUI/models/checkpoints/flux1-dev-fp8.safetensors`

### Out of Memory (CUDA OOM)
```
CUDA out of memory
```
**Fixes:**
- Reduce resolution to 768x768 (change node 4 inputs)
- Use `--lowvram` flag when launching ComfyUI
- Reduce batch_size to 1 (already set)
- Close other GPU applications

### FluxGuidance Node Not Found
```
Error: Unknown node type 'FluxGuidance'
```
**Fix:** Update ComfyUI to v0.2.0+ or install the latest version:
```bash
git pull
python main.py
```

### Slow Generation
- Flux.1 Dev FP8 takes ~30-60 seconds on a 4090
- On lower VRAM GPUs (3060/4060), expect 2-5 minutes
- Consider using `--force-fp16` flag

---

## 6. Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                   AETHER AI Pipeline                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  User Request                                                 │
│  (product description + style)                                │
│       │                                                       │
│       ▼                                                       │
│  ┌──────────┐    ┌──────────────────┐    ┌──────────────┐   │
│  │ Template  │───►│ Workflow JSON    │───►│ ComfyUI API  │   │
│  │ Engine    │    │ (node override)  │    │ /prompt      │   │
│  └──────────┘    └──────────────────┘    └──────┬───────┘   │
│                                                  │            │
│                                                  ▼            │
│                                          ┌──────────────┐   │
│                                          │ Flux.1 Dev    │   │
│                                          │ FP8 Inference │   │
│                                          └──────┬───────┘   │
│                                                  │            │
│                                                  ▼            │
│                                          ┌──────────────┐   │
│                                          │ Output PNG    │   │
│                                          │ (ComfyUI/     │   │
│                                          │  output/)     │   │
│                                          └──────────────┘   │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 7. Production Deployment

### Docker (Recommended)
```bash
# Run ComfyUI in Docker with GPU support
docker run -d \
  --gpus all \
  -p 8188:8188 \
  -v /path/to/models:/ComfyUI/models \
  -v /path/to/output:/ComfyUI/output \
  comfyui/comfyui:latest
```

### RunPod / Cloud
1. Deploy ComfyUI template from RunPod template library
2. Upload workflow JSONs to the instance
3. Use the API endpoint for automated generation
4. Mount cloud storage (S3/Wasabi) for output persistence

### Scaling
- Each ComfyUI instance handles one generation at a time
- Scale horizontally by running multiple instances behind a load balancer
- For burst capacity, use RunPod serverless or Banana Serverless

---

*Documentation for AETHER AI Product Photography Pipeline v1.0*
*Last updated: 2026-05-22*
