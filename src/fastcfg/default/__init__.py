from fastcfg import Config
from fastcfg.cache.policies import TEN_MIN_TTL
from fastcfg.backoff.policies import BASIC_BACKOFF_POLICY

# So Meta!
defaults = Config(cache_policy=TEN_MIN_TTL,
                  backoff_policy=BASIC_BACKOFF_POLICY)
