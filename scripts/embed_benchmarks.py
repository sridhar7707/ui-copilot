"""
Offline script — pre-compute CLIP embeddings for the benchmark library.

Usage:
    python scripts/embed_benchmarks.py

Expected directory layout:
    data/benchmarks/images/
        excellent/
            cards/
                stripe_card_001.png
                stripe_card_001.json   ← metadata (same stem)
            tables/
            dashboards/
            ...
        poor/
            (same category structure)

Output:
    data/benchmarks/embeddings.npz
        embeddings  — float32 (N, 512) — one row per image
        metadata    — object (N,)      — serialised JSON strings

Run this whenever images are added or changed.  The app reads only the .npz
file at runtime; raw images are never committed (see .gitignore).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = ROOT / "data" / "benchmarks" / "images"
OUTPUT = ROOT / "data" / "benchmarks" / "embeddings.npz"


def main() -> None:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("ERROR: sentence-transformers is not installed.")
        print("       pip install sentence-transformers")
        sys.exit(1)

    if not IMAGES_DIR.exists():
        print(f"ERROR: {IMAGES_DIR} does not exist.")
        print("       Place benchmark images under data/benchmarks/images/")
        sys.exit(1)

    image_exts = {".png", ".jpg", ".jpeg", ".webp"}
    image_paths = [
        p for p in IMAGES_DIR.rglob("*")
        if p.suffix.lower() in image_exts
    ]

    if not image_paths:
        print(f"No images found under {IMAGES_DIR}")
        sys.exit(1)

    print(f"Found {len(image_paths)} images — loading CLIP model…")
    model = SentenceTransformer("clip-ViT-B-32")

    from PIL import Image

    embeddings: list[np.ndarray] = []
    metadata: list[str] = []
    skipped = 0

    for path in sorted(image_paths):
        meta_path = path.with_suffix(".json")
        if not meta_path.exists():
            print(f"  SKIP {path.name} — no matching .json metadata file")
            skipped += 1
            continue

        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)

        # Infer quality from directory structure if not in JSON
        if "quality" not in meta:
            parts = path.parts
            if "excellent" in parts:
                meta["quality"] = "excellent"
            elif "poor" in parts:
                meta["quality"] = "poor"

        try:
            img = Image.open(path).convert("RGB")
            emb = np.array(model.encode(img), dtype=np.float32)
        except Exception as exc:
            print(f"  SKIP {path.name} — {exc}")
            skipped += 1
            continue

        embeddings.append(emb)
        metadata.append(json.dumps(meta))
        print(f"  OK   {path.name} ({meta.get('product', '?')} / {meta.get('category', '?')})")

    if not embeddings:
        print("No embeddings produced — nothing to save.")
        sys.exit(1)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        str(OUTPUT),
        embeddings=np.stack(embeddings),
        metadata=np.array(metadata, dtype=object),
    )
    print(f"\nSaved {len(embeddings)} embeddings → {OUTPUT}")
    if skipped:
        print(f"Skipped {skipped} files (missing metadata or load error)")


if __name__ == "__main__":
    main()
