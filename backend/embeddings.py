# embeddings.py — Mnemox Vector Embedding Engine
# Step 4: Generate embeddings via OpenAI text-embedding-3-small
# Cost: ~$0.02 per 1M tokens — virtually free for personal use

from openai import AsyncOpenAI
from config import get_settings
import hashlib
import logging

logger = logging.getLogger(__name__)

# ── Client (singleton) ────────────────────────────────────────────────────────
_client: AsyncOpenAI | None = None

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536

# In-memory cache: avoid re-embedding identical text
# Key: sha256(text), Value: list[float]
_embedding_cache: dict[str, list[float]] = {}


def get_openai_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY must be set in .env")
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


def _cache_key(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


async def embed_text(text: str) -> list[float]:
    """
    Generate a 1536-dim embedding vector for the given text.
    Uses in-memory cache to avoid duplicate API calls.
    """
    key = _cache_key(text)

    if key in _embedding_cache:
        logger.debug(f"Embedding cache hit for key {key[:8]}...")
        return _embedding_cache[key]

    client = get_openai_client()
    response = await client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text.strip(),
        encoding_format="float",
    )

    vector = response.data[0].embedding
    _embedding_cache[key] = vector

    logger.info(f"Embedding generated: {len(vector)} dims, text length {len(text)}")
    return vector


async def embed_batch(texts: list[str]) -> list[list[float]]:
    """
    Embed multiple texts in a single API call (more efficient).
    Returns list of vectors in same order as input.
    """
    if not texts:
        return []

    # Separate cached vs uncached
    keys = [_cache_key(t) for t in texts]
    uncached_indices = [i for i, k in enumerate(keys) if k not in _embedding_cache]
    uncached_texts = [texts[i] for i in uncached_indices]

    if uncached_texts:
        client = get_openai_client()
        response = await client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=uncached_texts,
            encoding_format="float",
        )
        for i, embedding_data in zip(uncached_indices, response.data):
            _embedding_cache[keys[i]] = embedding_data.embedding

    return [_embedding_cache[k] for k in keys]
