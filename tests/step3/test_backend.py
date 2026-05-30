"""
Step 3 Tests — FastAPI Backend + Supabase Storage
Run: python -m pytest tests/step3/ -v
All must pass before: git tag v0.3
"""

import os
import sys
import json
import pytest

BACKEND = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')


def read(filename):
    with open(os.path.join(BACKEND, filename)) as f:
        return f.read()


# ── File existence ────────────────────────────────────────────────────────────

def test_main_py_exists():
    assert os.path.exists(os.path.join(BACKEND, 'main.py'))

def test_models_py_exists():
    assert os.path.exists(os.path.join(BACKEND, 'models.py'))

def test_database_py_exists():
    assert os.path.exists(os.path.join(BACKEND, 'database.py'))

def test_config_py_exists():
    assert os.path.exists(os.path.join(BACKEND, 'config.py'))

def test_requirements_exists():
    assert os.path.exists(os.path.join(BACKEND, 'requirements.txt'))

def test_env_example_exists():
    assert os.path.exists(os.path.join(BACKEND, '.env.example'))

def test_supabase_schema_exists():
    assert os.path.exists(os.path.join(BACKEND, 'supabase_schema.sql'))


# ── Requirements ──────────────────────────────────────────────────────────────

def test_requirements_has_fastapi():
    assert 'fastapi' in read('requirements.txt').lower()

def test_requirements_has_supabase():
    assert 'supabase' in read('requirements.txt').lower()

def test_requirements_has_uvicorn():
    assert 'uvicorn' in read('requirements.txt').lower()

def test_requirements_has_pydantic():
    assert 'pydantic' in read('requirements.txt').lower()


# ── main.py routes ────────────────────────────────────────────────────────────

def test_health_endpoint_exists():
    assert '/health' in read('main.py')

def test_memories_post_endpoint():
    assert 'POST' in read('main.py') or '@app.post' in read('main.py')

def test_memories_get_endpoint():
    assert '@app.get' in read('main.py')

def test_memories_delete_endpoint():
    assert '@app.delete' in read('main.py')

def test_cors_middleware_configured():
    assert 'CORSMiddleware' in read('main.py')

def test_api_key_auth_present():
    assert 'verify_api_key' in read('main.py') or 'get_current_user' in read('main.py')

def test_no_hardcoded_secrets():
    suspicious = ['sk-', 'eyJ', 'Bearer=', 'Bearer =']
    code = read('main.py')
    for s in suspicious:
        assert s not in code, f"Possible secret: {s}"


# ── models.py ─────────────────────────────────────────────────────────────────

def test_memory_create_model():
    assert 'MemoryCreate' in read('models.py')

def test_memory_response_model():
    assert 'MemoryResponse' in read('models.py')

def test_source_validation():
    # Source field must validate against allowed AI tools
    assert 'chatgpt' in read('models.py')
    assert 'claude' in read('models.py')
    assert 'gemini' in read('models.py')
    assert 'copilot' in read('models.py')

def test_health_response_model():
    assert 'HealthResponse' in read('models.py')


# ── database.py ───────────────────────────────────────────────────────────────

def test_save_memory_function():
    assert 'save_memory' in read('database.py')

def test_get_memories_function():
    assert 'get_memories' in read('database.py')

def test_delete_memory_function():
    assert 'delete_memory' in read('database.py')

def test_health_check_db_function():
    assert 'health_check_db' in read('database.py')

def test_supabase_client_singleton():
    assert 'get_supabase' in read('database.py')


# ── config.py ────────────────────────────────────────────────────────────────

def test_settings_class_exists():
    assert 'Settings' in read('config.py')

def test_supabase_url_in_config():
    assert 'supabase_url' in read('config.py')

def test_api_secret_key_in_config():
    assert 'api_secret_key' in read('config.py')

def test_cors_origins_in_config():
    assert 'cors_origins' in read('config.py')


# ── SQL schema ────────────────────────────────────────────────────────────────

def test_schema_has_memories_table():
    assert 'CREATE TABLE' in read('supabase_schema.sql')
    assert 'memories' in read('supabase_schema.sql')

def test_schema_has_rls():
    assert 'ROW LEVEL SECURITY' in read('supabase_schema.sql')

def test_schema_has_indexes():
    assert 'CREATE INDEX' in read('supabase_schema.sql')

def test_env_example_has_supabase_vars():
    env = read('.env.example')
    assert 'SUPABASE_URL' in env
    assert 'SUPABASE_SERVICE_KEY' in env
    assert 'API_SECRET_KEY' in env
