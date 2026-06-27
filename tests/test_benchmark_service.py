"""
Module 3b — Benchmark Library tests.

All tests are deterministic: no model downloads, no disk images.
The pure cosine_top_k function is tested directly; score() is tested
by monkey-patching the module globals.
"""
from __future__ import annotations

import numpy as np
import pytest

from backend.services import benchmark_service


# ── cosine_top_k (pure math — no model needed) ────────────────────────────────

class TestCosineTopK:
    def _unit(self, v: list[float]) -> np.ndarray:
        a = np.array(v, dtype=np.float32)
        return a / np.linalg.norm(a)

    def test_returns_closest_vector(self):
        library = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ], dtype=np.float32)
        query = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        idx, sims = benchmark_service.cosine_top_k(query, library, k=1)
        assert idx[0] == 0
        assert sims[0] == pytest.approx(1.0, abs=1e-5)

    def test_top_k_sorted_descending(self):
        library = np.eye(4, dtype=np.float32)  # 4 orthogonal unit vectors
        query = np.array([0.9, 0.3, 0.1, 0.0], dtype=np.float32)
        idx, sims = benchmark_service.cosine_top_k(query, library, k=3)
        assert list(sims) == sorted(sims, reverse=True)

    def test_k_capped_at_library_size(self):
        library = np.eye(2, dtype=np.float32)
        query = np.array([1.0, 0.0], dtype=np.float32)
        idx, sims = benchmark_service.cosine_top_k(query, library, k=10)
        assert len(idx) == 2

    def test_identical_vectors_score_1(self):
        v = np.array([0.5, 0.5, 0.5, 0.5], dtype=np.float32)
        idx, sims = benchmark_service.cosine_top_k(v, v.reshape(1, -1), k=1)
        assert sims[0] == pytest.approx(1.0, abs=1e-5)

    def test_orthogonal_vectors_score_0(self):
        library = np.array([[0.0, 1.0]], dtype=np.float32)
        query = np.array([1.0, 0.0], dtype=np.float32)
        idx, sims = benchmark_service.cosine_top_k(query, library, k=1)
        assert sims[0] == pytest.approx(0.0, abs=1e-5)

    def test_zero_query_vector_no_crash(self):
        library = np.eye(3, dtype=np.float32)
        query = np.zeros(3, dtype=np.float32)
        idx, sims = benchmark_service.cosine_top_k(query, library, k=2)
        assert len(idx) == 2  # shouldn't raise

    def test_multiple_embeddings_correct_ranking(self):
        library = np.array([
            [1.0, 0.0],   # idx 0 — closest to query
            [0.0, 1.0],   # idx 1 — orthogonal
            [0.7, 0.7],   # idx 2 — 45°
        ], dtype=np.float32)
        query = np.array([1.0, 0.0], dtype=np.float32)
        idx, sims = benchmark_service.cosine_top_k(query, library, k=3)
        assert idx[0] == 0   # most similar
        assert idx[1] == 2   # second


# ── diff_notes ────────────────────────────────────────────────────────────────

class TestDiffNotes:
    def test_negative_attributes_become_notes(self):
        meta = {"attributes": {"spacing": "cramped", "typography": "poor"}}
        notes = benchmark_service._diff_notes(meta)
        assert len(notes) == 2
        assert any("spacing" in n for n in notes)
        assert any("typography" in n for n in notes)

    def test_positive_attributes_not_flagged(self):
        meta = {"attributes": {"spacing": "excellent", "contrast": "excellent"}}
        notes = benchmark_service._diff_notes(meta)
        assert notes == []

    def test_capped_at_3(self):
        meta = {"attributes": {f"attr{i}": "poor" for i in range(10)}}
        notes = benchmark_service._diff_notes(meta)
        assert len(notes) == 3

    def test_empty_attributes(self):
        assert benchmark_service._diff_notes({}) == []
        assert benchmark_service._diff_notes({"attributes": {}}) == []


# ── score() with injected data (no real model) ───────────────────────────────

class TestScoreWithMockData:
    """
    Inject fake embeddings and metadata into the module's private globals
    to test the scoring pipeline end-to-end without a real model or images.
    """

    def _fake_embs(self) -> np.ndarray:
        return np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.7, 0.7, 0.0, 0.0],
        ], dtype=np.float32)

    def _fake_meta(self) -> list[dict]:
        return [
            {"id": "stripe_001", "product": "Stripe", "category": "cards",
             "quality": "excellent", "quality_score": 96, "attributes": {"spacing": "excellent"}},
            {"id": "poor_001", "product": "anti-pattern", "category": "cards",
             "quality": "poor", "quality_score": 30, "attributes": {"spacing": "cramped"}},
            {"id": "linear_001", "product": "Linear", "category": "dashboards",
             "quality": "excellent", "quality_score": 92, "attributes": {}},
        ]

    def _fake_model(self, query_vec: np.ndarray):
        """Minimal duck-type model that returns a preset embedding."""
        class _M:
            def encode(self_, img):  # noqa: N805
                return query_vec
        return _M()

    def _inject(self, query_vec: np.ndarray, monkeypatch):
        monkeypatch.setattr(benchmark_service, "_embeddings", self._fake_embs())
        monkeypatch.setattr(benchmark_service, "_meta", self._fake_meta())
        monkeypatch.setattr(benchmark_service, "_loaded", True)
        monkeypatch.setattr(benchmark_service, "_model", self._fake_model(query_vec))

    def test_returns_available_true(self, monkeypatch):
        query = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
        self._inject(query, monkeypatch)
        # Provide minimal valid PNG bytes so PIL doesn't error
        import io
        from PIL import Image
        buf = io.BytesIO()
        Image.new("RGB", (10, 10), color=(128, 128, 128)).save(buf, format="PNG")
        result = benchmark_service.score(buf.getvalue(), top_k=3)
        assert result["available"] is True

    def test_closest_product_is_stripe(self, monkeypatch):
        # Query pointing at first embedding (Stripe)
        query = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
        self._inject(query, monkeypatch)
        import io
        from PIL import Image
        buf = io.BytesIO()
        Image.new("RGB", (10, 10)).save(buf, format="PNG")
        result = benchmark_service.score(buf.getvalue(), top_k=1)
        assert result["closest_product"] == "Stripe"

    def test_top_matches_sorted_by_similarity(self, monkeypatch):
        query = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
        self._inject(query, monkeypatch)
        import io
        from PIL import Image
        buf = io.BytesIO()
        Image.new("RGB", (10, 10)).save(buf, format="PNG")
        result = benchmark_service.score(buf.getvalue(), top_k=3)
        sims = [m["similarity"] for m in result["top_matches"]]
        assert sims == sorted(sims, reverse=True)

    def test_no_model_returns_available_false(self, monkeypatch):
        monkeypatch.setattr(benchmark_service, "_model", None)
        monkeypatch.setattr(benchmark_service, "_loaded", True)
        import io
        from PIL import Image
        buf = io.BytesIO()
        Image.new("RGB", (10, 10)).save(buf, format="PNG")
        result = benchmark_service.score(buf.getvalue())
        assert result["available"] is False

    def test_no_embeddings_returns_available_false(self, monkeypatch):
        query = np.array([1.0, 0.0], dtype=np.float32)
        monkeypatch.setattr(benchmark_service, "_model", self._fake_model(query))
        monkeypatch.setattr(benchmark_service, "_embeddings", None)
        monkeypatch.setattr(benchmark_service, "_meta", None)
        monkeypatch.setattr(benchmark_service, "_loaded", True)
        import io
        from PIL import Image
        buf = io.BytesIO()
        Image.new("RGB", (10, 10)).save(buf, format="PNG")
        result = benchmark_service.score(buf.getvalue())
        assert result["available"] is False


# ── available() ───────────────────────────────────────────────────────────────

class TestAvailable:
    def test_false_when_no_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(benchmark_service, "_EMBEDDINGS_PATH",
                            tmp_path / "nonexistent.npz")
        assert benchmark_service.available() is False

    def test_true_when_file_exists(self, tmp_path, monkeypatch):
        f = tmp_path / "embeddings.npz"
        f.touch()
        monkeypatch.setattr(benchmark_service, "_EMBEDDINGS_PATH", f)
        assert benchmark_service.available() is True
