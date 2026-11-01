#!/usr/bin/env python3
"""
Context Manager for red-tide-algal-bloom-monitoring Skill
Manages context window and token consumption for efficient processing
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json


@dataclass
class ContextMetrics:
    """Metrics for context usage"""
    total_tokens: int
    input_tokens: int
    output_tokens: int
    compression_ratio: float
    cache_hit_rate: float
    estimated_cost_usd: float


class TokenEstimator:
    """Estimate token count for text without API calls"""

    # Approximate token ratios (1 token ≈ X characters)
    CHAR_TO_TOKEN_RATIO = 4.0  # For English text
    WORD_TO_TOKEN_RATIO = 0.75  # For English text

    # Language-specific ratios
    LANGUAGE_RATIOS = {
        'en': 0.75,  # English
        'vi': 0.85,  # Vietnamese (more syllables per word)
        'zh': 0.5,   # Chinese (characters map closer to tokens)
        'ja': 0.5,   # Japanese
        'ko': 0.7,   # Korean
        'es': 0.8,   # Spanish
        'fr': 0.8,   # French
        'de': 0.85,  # German
        'default': 0.75
    }

    @classmethod
    def estimate_tokens(cls, text: str, language: str = 'en') -> int:
        """Estimate token count for text"""
        if not text:
            return 0

        # Try language-specific word-based estimation
        ratio = cls.LANGUAGE_RATIOS.get(language, cls.LANGUAGE_RATIOS['default'])
        word_count = len(text.split())

        # Also consider character-based estimation as a check
        char_estimate = len(text) / cls.CHAR_TO_TOKEN_RATIO
        word_estimate = word_count * ratio

        # Use the average of both methods
        return int((char_estimate + word_estimate) / 2)

    @classmethod
    def estimate_message_tokens(cls, message: Dict[str, Any]) -> int:
        """Estimate tokens for a complete message"""
        # Estimate role
        role_tokens = len(message.get('role', '')) / cls.CHAR_TO_TOKEN_RATIO

        # Estimate content
        content = message.get('content', '')
        content_tokens = cls.estimate_tokens(content)

        # Add overhead for JSON formatting
        overhead = 10

        return int(role_tokens + content_tokens + overhead)

    @classmethod
    def estimate_messages_tokens(cls, messages: List[Dict[str, Any]]) -> int:
        """Estimate total tokens for a list of messages"""
        return sum(cls.estimate_message_tokens(msg) for msg in messages)


class ContentCompressor:
    """Compress content to reduce token usage while preserving information"""

    # Patterns for redundancy detection
    REDUNDANT_PATTERNS = [
        (r'([A-Z][a-z]+)\s+\1\s+', r'\1 '),  # Repeated words
        (r'(\w+\s+){5,}(\w+\s+)', r'... '),   # Long repetitive sequences
    ]

    # Stop words (common words that can be removed in some contexts)
    STOP_WORDS = set([
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
        'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
    ])

    @classmethod
    def remove_redundancy(cls, text: str) -> str:
        """Remove redundant patterns from text"""
        for pattern, replacement in cls.REDUNDANT_PATTERNS:
            text = re.sub(pattern, replacement, text)
        return text

    @classmethod
    def remove_stop_words(cls, text: str, preserve_structure: bool = True) -> str:
        """Remove stop words from text (carefully, to preserve meaning)"""
        if preserve_structure:
            # Only remove stop words in less critical positions
            words = text.split()
            filtered = []
            for i, word in enumerate(words):
                word_lower = word.lower().strip('.,!?;:')
                if word_lower not in cls.STOP_WORDS or i % 3 == 0:
                    filtered.append(word)
            return ' '.join(filtered)
        else:
            words = text.split()
            filtered = [w for w in words if w.lower().strip('.,!?;:') not in cls.STOP_WORDS]
            return ' '.join(filtered)

    @classmethod
    def summarize_numeric_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize numeric data to reduce token count"""
        summarized = {}
        for key, value in data.items():
            if isinstance(value, (int, float)):
                # Round to significant figures
                if isinstance(value, float):
                    summarized[key] = round(value, 3)
                else:
                    summarized[key] = value
            elif isinstance(value, dict):
                summarized[key] = cls.summarize_numeric_data(value)
            elif isinstance(value, list):
                if len(value) > 10:
                    # Sample large lists
                    sample_size = max(5, int(len(value) ** 0.5))
                    step = len(value) // sample_size
                    summarized[key] = [value[i] for i in range(0, len(value), step)]
                else:
                    summarized[key] = value
            else:
                summarized[key] = value
        return summarized

    @classmethod
    def compress_content(cls, content: str, target_ratio: float = 0.3, language: str = 'en') -> str:
        """Compress content to target ratio while preserving key information"""
        original_tokens = TokenEstimator.estimate_tokens(content, language)
        target_tokens = int(original_tokens * target_ratio)

        if original_tokens <= target_tokens:
            return content

        # Priority-based compression
        compressed = content

        # Step 1: Remove redundancy
        compressed = cls.remove_redundancy(compressed)
        current_tokens = TokenEstimator.estimate_tokens(compressed, language)

        if current_tokens <= target_tokens:
            return compressed

        # Step 2: Remove some stop words (preserve structure)
        compressed = cls.remove_stop_words(compressed, preserve_structure=True)
        current_tokens = TokenEstimator.estimate_tokens(compressed, language)

        if current_tokens <= target_tokens:
            return compressed

        # Step 3: Extractive summarization (keep key sentences).
        # Each scored item carries its original index so we can restore
        # reading order after selecting the highest-scoring sentences,
        # without re-querying the (dot-stripped) sentence list.
        sentences = re.split(r'([.!?]+)', compressed)
        # Recombine sentence text with its trailing punctuation so scoring
        # operates on complete sentences and order is preserved by index.
        scored_units = []
        j = 0
        while j < len(sentences):
            text = sentences[j]
            punct = sentences[j + 1] if j + 1 < len(sentences) else ''
            j += 2
            if not text.strip():
                continue
            scored_units.append((len(scored_units), text.strip(), punct))

        sentence_scores = []
        for i, (orig_idx, text, punct) in enumerate(scored_units):
            score = 0.0

            # Position: earlier sentences are often more important
            score += (len(scored_units) - i) * 0.1

            # Length: prefer moderate length sentences
            words = len(text.split())
            if 5 <= words <= 25:
                score += 1

            # Key terms (domain-specific)
            key_terms = ['bloom', 'toxin', 'risk', 'alert', 'monitoring',
                         'chlorophyll', 'satellite', 'aquaculture', 'harvest']
            if any(term in text.lower() for term in key_terms):
                score += 2

            sentence_scores.append((orig_idx, text, punct, score))

        # Keep top sentences, then restore original reading order
        sentence_scores.sort(key=lambda x: x[3], reverse=True)
        keep_ratio = target_ratio if target_ratio < 0.5 else 0.5
        keep_count = max(3, int(len(sentence_scores) * keep_ratio))
        kept = sorted(sentence_scores[:keep_count], key=lambda x: x[0])

        return ''.join(f"{text}{punct} " for _, text, punct, _ in kept).strip()


class CacheEntry:
    """Cache entry with TTL"""

    def __init__(self, key: str, value: Any, ttl: int = 300):
        self.key = key
        self.value = value
        self.created_at = datetime.utcnow()
        self.ttl = ttl
        self.hits = 0

    def is_expired(self) -> bool:
        """Check if entry has expired"""
        return (datetime.utcnow() - self.created_at).total_seconds() > self.ttl

    def hit(self):
        """Record a cache hit"""
        self.hits += 1


class CacheManager:
    """Multi-level cache for repeated content access"""

    def __init__(self):
        self.l1_cache: Dict[str, CacheEntry] = {}  # In-memory cache
        self.l2_enabled = False  # File cache (optional)
        self.l2_path = None
        self.stats = {
            'l1_hits': 0,
            'l1_misses': 0,
            'l2_hits': 0,
            'l2_misses': 0,
            'evictions': 0
        }
        self.max_l1_entries = 1000

    def _generate_key(self, content: str) -> str:
        """Generate cache key from content"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def get(self, content: str) -> Optional[Any]:
        """Get cached content"""
        key = self._generate_key(content)

        # Check L1 cache
        if key in self.l1_cache:
            entry = self.l1_cache[key]
            if not entry.is_expired():
                entry.hit()
                self.stats['l1_hits'] += 1
                return entry.value
            else:
                # Remove expired entry
                del self.l1_cache[key]
                self.stats['evictions'] += 1

        self.stats['l1_misses'] += 1
        return None

    def set(self, content: str, value: Any, ttl: int = 300):
        """Set cached content"""
        key = self._generate_key(content)

        # Evict oldest entries if cache is full
        if len(self.l1_cache) >= self.max_l1_entries:
            oldest_key = min(self.l1_cache.keys(),
                           key=lambda k: self.l1_cache[k].created_at)
            del self.l1_cache[oldest_key]
            self.stats['evictions'] += 1

        self.l1_cache[key] = CacheEntry(key, value, ttl)

    def invalidate(self, pattern: Optional[str] = None):
        """Invalidate cache entries"""
        if pattern:
            # Invalidate entries matching pattern (simple key matching)
            keys_to_remove = [k for k in self.l1_cache.keys() if pattern in k]
            for k in keys_to_remove:
                del self.l1_cache[k]
                self.stats['evictions'] += 1
        else:
            # Clear all cache
            count = len(self.l1_cache)
            self.l1_cache.clear()
            self.stats['evictions'] += count

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        l1_total = self.stats['l1_hits'] + self.stats['l1_misses']
        l1_hit_rate = self.stats['l1_hits'] / l1_total if l1_total > 0 else 0

        return {
            'l1_entries': len(self.l1_cache),
            'l1_hit_rate': l1_hit_rate,
            'l1_hits': self.stats['l1_hits'],
            'l1_misses': self.stats['l1_misses'],
            'evictions': self.stats['evictions']
        }

    def clear_expired(self):
        """Clear expired entries"""
        expired_keys = [k for k, v in self.l1_cache.items() if v.is_expired()]
        for k in expired_keys:
            del self.l1_cache[k]
            self.stats['evictions'] += 1


class ContextManager:
    """Manage context window and token consumption"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        default_config = {
            'window_size': 200000,
            'reserved_output_tokens': 4096,
            'max_input_tokens': 159804,
            'enable_caching': True,
            'cache_ttl_seconds': 300,
            'enable_compression': True,
            'target_compression_ratio': 0.3
        }
        self.config = {**default_config, **(config or {})}

        self.cache = CacheManager() if self.config['enable_caching'] else None
        self.compressor = ContentCompressor()
        self.estimator = TokenEstimator()

    def estimate_tokens(self, text: str, language: str = 'en') -> int:
        """Estimate token count for text"""
        return self.estimator.estimate_tokens(text, language)

    def estimate_messages_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """Estimate tokens for messages"""
        return self.estimator.estimate_messages_tokens(messages)

    def optimize_context(self, messages: List[Dict[str, Any]], language: str = 'en') -> List[Dict[str, Any]]:
        """Optimize context for token efficiency"""
        if not self.config['enable_compression']:
            return messages

        current_tokens = self.estimate_messages_tokens(messages)
        max_tokens = self.config['max_input_tokens']

        if current_tokens <= max_tokens:
            return messages

        # Optimization strategy
        target_ratio = max_tokens / current_tokens
        optimized_messages = []

        for message in messages:
            optimized = message.copy()
            content = message.get('content', '')

            # Compress content
            if content:
                compressed = self.compressor.compress_content(
                    content,
                    target_ratio=target_ratio,
                    language=language
                )
                optimized['content'] = compressed

            optimized_messages.append(optimized)

        return optimized_messages

    def apply_compression(self, text: str, language: str = 'en') -> str:
        """Compress text to target ratio"""
        if not self.config['enable_compression']:
            return text

        return self.compressor.compress_content(
            text,
            target_ratio=self.config['target_compression_ratio'],
            language=language
        )

    def get_from_cache(self, content: str) -> Optional[Any]:
        """Get content from cache"""
        if not self.cache:
            return None
        return self.cache.get(content)

    def set_cache(self, content: str, value: Any):
        """Set content in cache"""
        if not self.cache:
            return
        self.cache.set(content, value, ttl=self.config['cache_ttl_seconds'])

    def invalidate_cache(self, pattern: Optional[str] = None):
        """Invalidate cache entries"""
        if not self.cache:
            return
        self.cache.invalidate(pattern)

    def get_metrics(self) -> ContextMetrics:
        """Get context usage metrics"""
        cache_stats = self.cache.get_stats() if self.cache else {}

        return ContextMetrics(
            total_tokens=0,  # To be calculated during processing
            input_tokens=0,
            output_tokens=0,
            compression_ratio=self.config['target_compression_ratio'],
            cache_hit_rate=cache_stats.get('l1_hit_rate', 0.0),
            estimated_cost_usd=0.0  # To be calculated
        )

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.cache:
            return {}
        return self.cache.get_stats()

    def clear_expired_cache(self):
        """Clear expired cache entries"""
        if not self.cache:
            return
        self.cache.clear_expired()


# Global context manager instance
_context_manager: Optional[ContextManager] = None


def get_context_manager(config: Optional[Dict[str, Any]] = None) -> ContextManager:
    """Get global context manager instance"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager(config)
    return _context_manager


def reset_context_manager():
    """Reset global context manager"""
    global _context_manager
    _context_manager = None


if __name__ == "__main__":
    # Test context manager
    manager = ContextManager()

    # Test token estimation
    test_text = "This is a test of the token estimation system."
    estimated = manager.estimate_tokens(test_text)
    print(f"Estimated tokens for test text: {estimated}")

    # Test compression
    long_text = " ".join(["This is a test sentence."] * 100)
    compressed = manager.apply_compression(long_text)
    print(f"Original: {len(long_text)} chars, Compressed: {len(compressed)} chars")

    # Test cache
    manager.set_cache("test_key", {"result": "test_value"})
    cached = manager.get_from_cache("test_key")
    print(f"Cached value: {cached}")

    # Get stats
    stats = manager.get_cache_stats()
    print(f"Cache stats: {stats}")
