import pytest
from app.services.retrieval_service import _reciprocal_rank_fusion


def test_rrf_empty_inputs():
    result = _reciprocal_rank_fusion([], [])
    assert result == []


def test_rrf_dense_only():
    dense = [
        {"point_id": "a", "score": 0.9, "chunk_text": "text a"},
        {"point_id": "b", "score": 0.8, "chunk_text": "text b"},
    ]
    result = _reciprocal_rank_fusion(dense, [])
    assert len(result) == 2
    assert result[0]["point_id"] == "a"


def test_rrf_fusion_boosts_overlap():
    dense = [
        {"point_id": "a", "score": 0.9, "chunk_text": "text a"},
        {"point_id": "b", "score": 0.8, "chunk_text": "text b"},
    ]
    sparse = [
        {"point_id": "b", "bm25_score": 5.0, "chunk_text": "text b"},
        {"point_id": "c", "bm25_score": 4.0, "chunk_text": "text c"},
    ]
    result = _reciprocal_rank_fusion(dense, sparse)
    assert result[0]["point_id"] == "b"
