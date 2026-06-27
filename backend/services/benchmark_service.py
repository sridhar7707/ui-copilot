"""
Module 3b — Benchmark Library & Similarity Scoring.

Compares an uploaded screenshot against a curated library of reference UI
screenshots using pre-computed CLIP embeddings.  Falls back gracefully when
the library or model is unavailable.

Runtime data flow:
  1. Embeddings pre-computed offline via scripts/embed_benchmarks.py
  2. Loaded once at module level; kept resident in memory
  3. Each screenshot is embedded with CLIP → cosine similarity vs. library
  4. Top-3 matches returned with attribute diff notes

Requires: sentence-transformers (pip install sentence-transformers)
          data/benchmarks/embeddings.npz  (produced by the embed script)
"""
from __future__ import annotations

import io
import json
import logging
from pathlib import Path
from typing import Optional

import numpy as np

log = logging.getLogger(__name__)

_EMBEDDINGS_PATH = Path("data/benchmarks/embeddings.npz")
_METADATA_DIR = Path("data/benchmarks/metadata")

# ── module-level singletons (loaded once) ─────────────────────────────────────
_model = None          # SentenceTransformer | None
_embeddings: Optional[np.ndarray] = None  # (N, D) float32
_meta: Optional[list[dict]] = None        # parallel list of metadata dicts
_loaded = False        # guard against repeated failed loads


def prewarm() -> None:
    """Pre-load model and embeddings; call at app startup in a thread pool."""
    _load_model()
    _load_embeddings()


def available() -> bool:
    """True when embeddings exist on disk and can be loaded."""
    return _EMBEDDINGS_PATH.exists()


def score(image_bytes: bytes, top_k: int = 3) -> dict:
    """
    Score a screenshot against the benchmark library.

    Returns a dict with ``available: False`` when the library or model
    is not configured, so callers can include this in a response without
    raising an error.
    """
    model = _load_model()
    embs, meta = _load_embeddings()

    if model is None:
        return {"available": False, "reason": "sentence-transformers not installed"}
    if embs is None or not meta:
        return {"available": False, "reason": "benchmark embeddings not found — run scripts/embed_benchmarks.py"}

    try:
        from PIL import Image
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        query = np.array(model.encode(img), dtype=np.float32)
    except Exception as exc:
        log.warning("benchmark_service: could not embed image: %s", exc)
        return {"available": False, "reason": str(exc)}

    indices, similarities = cosine_top_k(query, embs, top_k)

    top_matches = []
    for idx, sim in zip(indices, similarities):
        m = meta[idx]
        top_matches.append({
            "id": m.get("id", ""),
            "product": m.get("product", ""),
            "category": m.get("category", ""),
            "quality": m.get("quality", "excellent"),
            "quality_score": m.get("quality_score"),
            "similarity": round(float(sim) * 100, 1),
            "diff_notes": _diff_notes(m),
        })

    best = top_matches[0] if top_matches else {}
    return {
        "available": True,
        "overall_similarity": best.get("similarity", 0.0),
        "closest_product": best.get("product", ""),
        "top_matches": top_matches,
    }


# ── pure similarity math (testable without a model) ──────────────────────────

def cosine_top_k(
    query: np.ndarray,
    library: np.ndarray,
    k: int = 3,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (indices, scores) of the top-k most similar rows in *library*.

    Both *query* (shape D) and *library* (shape N×D) are L2-normalised
    before the dot product so the result is cosine similarity in [-1, 1].
    """
    q = query / np.clip(np.linalg.norm(query), 1e-9, None)
    norms = np.linalg.norm(library, axis=1, keepdims=True)
    normed = library / np.clip(norms, 1e-9, None)
    sims = normed @ q
    actual_k = min(k, len(sims))
    top_idx = np.argsort(sims)[::-1][:actual_k]
    return top_idx, sims[top_idx]


# ── lazy loaders ──────────────────────────────────────────────────────────────

def _load_model():
    global _model
    if _model is not None:
        return _model
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("clip-ViT-B-32")
        log.info("benchmark_service: CLIP model loaded")
    except Exception as exc:
        log.info("benchmark_service: model unavailable (%s)", exc)
        _model = None
    return _model


def _load_embeddings() -> tuple[Optional[np.ndarray], Optional[list[dict]]]:
    global _embeddings, _meta, _loaded
    if _loaded:
        return _embeddings, _meta
    _loaded = True
    if not _EMBEDDINGS_PATH.exists():
        return None, None
    try:
        data = np.load(str(_EMBEDDINGS_PATH), allow_pickle=True)
        _embeddings = data["embeddings"].astype(np.float32)
        _meta = [json.loads(m) if isinstance(m, str) else m for m in data["metadata"]]
        log.info("benchmark_service: loaded %d benchmark embeddings", len(_meta))
    except Exception as exc:
        log.warning("benchmark_service: could not load embeddings: %s", exc)
        _embeddings = None
        _meta = None
    return _embeddings, _meta


# ── helpers ───────────────────────────────────────────────────────────────────

_NEGATIVE_ATTRS = {"poor", "cramped", "overcrowded", "low", "inconsistent", "none"}


def _diff_notes(meta: dict) -> list[str]:
    """Generate up to 3 improvement hints from benchmark attribute metadata."""
    notes = []
    for key, val in meta.get("attributes", {}).items():
        if isinstance(val, str) and val.lower() in _NEGATIVE_ATTRS:
            notes.append(f"Improve {key.replace('_', ' ')}")
        if len(notes) == 3:
            break
    return notes
