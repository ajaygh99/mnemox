"""
Step 4 Tests — Vector Embeddings + Smart Memory Retrieval
Run: python -m pytest tests/step4/ -v
All must pass before: git tag v0.4
"""

import os
import pytest

BACKEND = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')

def read(filename):
    with open(os.path.join(BACKEND, filename)) as f:
        return f.read()


# ── File existence ────────────────────────────────────────────────────────────

def test_embeddings_py_exists():
    assert os.path.exists(os.path.join(BACKEND, 'embeddings.py'))

def test_vector_store_py_exists():
    assert os.path.exists(os.path.join(BACKEND, 'vector_store.py'))


# ── Requirements updated ──────────────────────────────────────────────────────

def test_openai_in_requirements():
    assert 'openai' in read('requirements.txt').lower()

def test_qdrant_in_requirements():
    assert 'qdrant' in read('requirements.txt').lower()


# ── Config updated ────────────────────────────────────────────────────────────

def test_openai_api_key_in_config():
    assert 'openai_api_key' in read('config.py')

def test_qdrant_url_in_config():
    assert 'qdrant_url' in read('config.py')

def test_qdrant_api_key_in_config():
    assert 'qdrant_api_key' in read('config.py')


# ── embeddings.py ─────────────────────────────────────────────────────────────

def test_embed_text_function():
    assert 'embed_text' in read('embeddings.py')

def test_embed_batch_function():
    assert 'embed_batch' in read('embeddings.py')

def test_embedding_cache_present():
    assert '_embedding_cache' in read('embeddings.py')

def test_embedding_model_defined():
    assert 'text-embedding-3-small' in read('embeddings.py')

def test_embedding_dimensions_defined():
    assert '1536' in read('embeddings.py')

def test_cache_key_uses_hash():
    assert 'sha256' in read('embeddings.py')

def test_no_hardcoded_openai_key():
    assert 'sk-' not in read('embeddings.py')


# ── vector_store.py ───────────────────────────────────────────────────────────

def test_ensure_collection_function():
    assert 'ensure_collection' in read('vector_store.py')

def test_upsert_memory_vector_function():
    assert 'upsert_memory_vector' in read('vector_store.py')

def test_search_similar_memories_function():
    assert 'search_similar_memories' in read('vector_store.py')

def test_delete_memory_vector_function():
    assert 'delete_memory_vector' in read('vector_store.py')

def test_health_check_vector_function():
    assert 'health_check_vector' in read('vector_store.py')

def test_collection_name_defined():
    assert 'mnemox_memories' in read('vector_store.py')

def test_cosine_distance_used():
    assert 'COSINE' in read('vector_store.py')

def test_score_threshold_parameter():
    assert 'score_threshold' in read('vector_store.py')

def test_in_memory_fallback():
    # Should support :memory: mode for dev/testing
    assert ':memory:' in read('vector_store.py')

def test_user_id_filter_supported():
    assert 'user_id' in read('vector_store.py')

def test_source_filter_supported():
    assert 'source' in read('vector_store.py')


# ── main.py updated ───────────────────────────────────────────────────────────

def test_search_endpoint_added():
    assert '/memories/search' in read('main.py')

def test_embed_text_called_on_save():
    assert 'embed_text' in read('main.py')

def test_upsert_called_on_save():
    assert 'upsert_memory_vector' in read('main.py')

def test_vector_deleted_on_remove():
    assert 'delete_memory_vector' in read('main.py')

def test_qdrant_health_in_health_endpoint():
    assert 'health_check_vector' in read('main.py')

def test_embedding_failure_is_nonfatal():
    # Embedding errors must be caught and logged, not crash the save
    assert 'embed_err' in read('main.py') or 'embedding failed' in read('main.py').lower()


# ── models.py updated ────────────────────────────────────────────────────────

def test_search_request_model():
    assert 'SearchRequest' in read('models.py')

def test_search_response_model():
    assert 'SearchResponse' in read('models.py')

def test_search_result_model():
    assert 'SearchResult' in read('models.py')

def test_score_threshold_in_search_request():
    assert 'score_threshold' in read('models.py')

def test_qdrant_connected_in_health():
    assert 'qdrant_connected' in read('models.py')


# ── env.example updated ──────────────────────────────────────────────────────

def test_openai_key_in_env_example():
    assert 'OPENAI_API_KEY' in read('.env.example')

def test_qdrant_url_in_env_example():
    assert 'QDRANT_URL' in read('.env.example')

def test_qdrant_api_key_in_env_example():
    assert 'QDRANT_API_KEY' in read('.env.example')
