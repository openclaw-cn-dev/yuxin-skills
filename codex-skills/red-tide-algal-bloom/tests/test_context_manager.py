"""Tests for scripts.context_manager (token estimation, compression, cache)."""
import pytest

from context_manager import (
    CacheManager,
    ContentCompressor,
    ContextManager,
    TokenEstimator,
)


def test_token_estimate_positive_and_language_aware():
    text = "The harmful algal bloom monitoring system tracks chlorophyll-a."
    en = TokenEstimator.estimate_tokens(text, "en")
    vi = TokenEstimator.estimate_tokens(text, "vi")
    assert en > 0
    assert vi >= en  # byte-heavy languages estimate equal or higher


def test_token_estimate_empty():
    assert TokenEstimator.estimate_tokens("", "en") == 0


def test_compression_preserves_key_terms():
    text = (
        "The satellite detected a harmful algal bloom with high chlorophyll. "
        "Aquaculture farms face elevated toxin risk this week. "
        "The bloom alert triggered harvest closure recommendations. "
        "Nutrient upwelling and warm SST are key environmental triggers. "
        "Routine monitoring continues across the coastal region. "
        "This sentence contains filler that is not very important for the analysis. "
        "Another filler sentence about the weather and unrelated topics today."
    )
    compressed = ContentCompressor.compress_content(text, target_ratio=0.4, language="en")
    assert isinstance(compressed, str)
    assert 0 < len(compressed) <= len(text)
    lowered = compressed.lower()
    # Extractive summarization must keep the most domain-relevant sentence(s).
    assert "bloom" in lowered or "chlorophyll" in lowered or "toxin" in lowered


def test_compression_short_text_returned_nonempty():
    short = "Bloom detected."
    out = ContentCompressor.compress_content(short, target_ratio=0.3, language="en")
    assert out.strip()


def test_context_manager_apply_compression_runs_without_error():
    mgr = ContextManager()
    long_text = " ".join(["The bloom risk is elevated."] * 50)
    compressed = mgr.apply_compression(long_text, language="en")
    assert isinstance(compressed, str)
    assert len(compressed) > 0


def test_cache_manager_set_get_round_trip():
    cache = CacheManager()
    cache.set("content-key-one", {"r": 1}, ttl=300)
    assert cache.get("content-key-one") == {"r": 1}
    stats = cache.get_stats()
    assert stats["l1_entries"] >= 1
    assert stats["l1_hits"] >= 1


def test_cache_manager_miss_returns_none():
    cache = CacheManager()
    assert cache.get("does-not-exist") is None
    stats = cache.get_stats()
    assert stats["l1_misses"] >= 1


def test_cache_manager_invalidate_all():
    cache = CacheManager()
    cache.set("a", 1, ttl=300)
    cache.set("b", 2, ttl=300)
    cache.invalidate()
    assert cache.get("a") is None
    assert cache.get("b") is None


def test_cache_manager_ttl_expiry():
    from datetime import datetime, timedelta
    cache = CacheManager()
    cache.set("ephemeral", "v", ttl=1)
    # Backdate the entry so it is unambiguously past its TTL.
    key = cache._generate_key("ephemeral")
    cache.l1_cache[key].created_at = datetime.utcnow() - timedelta(seconds=10)
    assert cache.get("ephemeral") is None
    assert cache.get("ephemeral") is None  # second get also misses (evicted)


def test_cache_manager_clear_expired():
    from datetime import datetime, timedelta
    cache = CacheManager()
    cache.set("fresh", 1, ttl=300)
    cache.set("stale", 2, ttl=60)
    stale_key = cache._generate_key("stale")
    cache.l1_cache[stale_key].created_at = datetime.utcnow() - timedelta(seconds=120)
    cache.clear_expired()
    assert cache.get("fresh") == 1
    assert cache.get("stale") is None


def test_context_manager_estimate_tokens_method():
    mgr = ContextManager()
    assert mgr.estimate_tokens("bloom monitoring", "en") > 0
