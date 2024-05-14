from fastcfg.cache.strategies import TTLCacheStrategy

TEN_MIN_TTL = TTLCacheStrategy(seconds=60*10)
