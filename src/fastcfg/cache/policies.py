"""
This module defines pre-configured cache policies for use with the caching mechanism.

Attributes:
    TEN_MIN_TTL (TTLCacheStrategy): A TTL (Time-To-Live) cache strategy with a 
    duration of 10 minutes.
    ONE_HOUR_TTL (TTLCacheStrategy): A TTL (Time-To-Live) cache strategy with a duration of 1 hour.
    DAILY_TTL (TTLCacheStrategy): A TTL (Time-To-Live) cache strategy with a duration of 1 day.
    LRU_POLICY (LRUCacheStrategy): A Least Recently Used (LRU) cache strategy 
    with a default capacity of 100 entries.
    MRU_POLICY (MRUCacheStrategy): A Most Recently Used (MRU) cache strategy
    with a default capacity of 100 entries.
"""

from fastcfg.cache.strategies import (
    LRUCacheStrategy,
    MRUCacheStrategy,
    TTLCacheStrategy,
)

TEN_MIN_TTL = TTLCacheStrategy(seconds=60 * 10)
ONE_HOUR_TTL = TTLCacheStrategy(seconds=60 * 60)
DAILY_TTL = TTLCacheStrategy(seconds=60 * 60 * 24)

LRU_POLICY = LRUCacheStrategy(capacity=100)
MRU_POLICY = MRUCacheStrategy(capacity=100)
