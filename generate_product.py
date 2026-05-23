#!/usr/bin/env python3
"""
AETHER AI - Automated Product Photography Pipeline
Usage:
  python generate_product.py "product description" [--style white_bg|studio|lifestyle|outdoor|automotive] [--seed 123456789]
  
Requires: ComfyUI running at localhost:8188
"""

import json, requests, time, sys, os, argparse

COMFY_HOST = "http://127.0.0.1:8188"
WORKFLOW_DIR = os.path.join(os.path.dirname(__file__), "comfyui_workflows")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "generated_images")

# ComfyUI output folder - resolves relative to ComfyUI install
_COMFY_DIR = os.path.abspath(os.path.join(WORKFLOW_DIR, "..", "..", "comfy", "ComfyUI"))
if not os.path.exists(os.path.join(_COMFY_DIR, "output")):
    _COMFY_DIR = WORKFLOW_DIR  # fallback

STYLE_MAP = {
    "white_bg": "white_background",
    "studio": "studio_lighting",
    "lifestyle": "lifestyle",
    "outdoor": "outdoor_natural",
    "automotive": "automotive",
}

def generate(description, style="white_bg", seed=None, timeout=600):
    workflow_file = STYLE_MAP.get(style, style)
    workflow_path = os.path.join(WORKFLOW_DIR, f"{workflow_file}.json")
    
    if not os.path.exists(workflow_path):
        raise FileNotFoundError(f"Workflow not found: {workflow_path}")
    
    with open(workflow_path) as f:
        wf = json.load(f)
    
    # Inject description into the prompt template
    prompt_template = wf["2"]["inputs"]["text"]
    wf["2"]["inputs"]["text"] = prompt_template.format(description)
    
    if seed is not None:
        wf["7"]["inputs"]["seed"] = seed
    
    # Submit to ComfyUI
    resp = requests.post(f"{COMFY_HOST}/prompt", json={"prompt": wf}, timeout=30)
    result = resp.json()
    
    if "prompt_id" not in result:
        raise RuntimeError(f"ComfyUI error: {result}")
    
    prompt_id = result["prompt_id"]
    print(f"[AETHER] Generating... ID: {prompt_id}")
    
    # Poll for completion
    start = time.time()
    for _ in range(timeout // 3):
        time.sleep(3)
        
        history = requests.get(f"{COMFY_HOST}/history/{prompt_id}", timeout=10).json()
        if history.get(prompt_id):
            data = history[prompt_id]
            outputs = data.get("outputs", {})
            images = []
            for node_id, node_out in outputs.items():
                for img in node_out.get("images", []):
                    # Check ComfyUI output dir first, then fallback
                    for base in [_COMFY_DIR, os.path.dirname(__file__)]:
                        candidate = os.path.join(base, "output", img["filename"])
                        if os.path.exists(candidate):
                            img_path = candidate
                            break
                    else:
                        img_path = os.path.join(_COMFY_DIR, "output", img["filename"])
                    images.append(img_path)
            
            elapsed = time.time() - start
            if images:
                # Copy to output dir
                os.makedirs(OUTPUT_DIR, exist_ok=True)
                local_paths = []
                for img_path in images:
                    dest = os.path.join(OUTPUT_DIR, os.path.basename(img_path))
                    import shutil
                    shutil.copy2(img_path, dest)
                    local_paths.append(dest)
                
                print(f"[AETHER] Done in {elapsed:.1f}s")
                return {"success": True, "images": local_paths, "prompt_id": prompt_id, "elapsed": elapsed}
            break
        
        # Check queue
        queue = requests.get(f"{COMFY_HOST}/queue", timeout=10).json()
        running = len(queue.get("queue_running", []))
        pending = len(queue.get("queue_pending", []))
        if running == 0 and pending == 0:
            break
    
    raise TimeoutError(f"Image generation timed out after {timeout}s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate product photography with AI")
    parser.add_argument("description", help="Product description")
    parser.add_argument("--style", choices=list(STYLE_MAP.keys()), default="white_bg",
                        help="Photography style")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    args = parser.parse_args()
    
    result = generate(args.description, args.style, args.seed)
    print(json.dumps(result, indent=2))
