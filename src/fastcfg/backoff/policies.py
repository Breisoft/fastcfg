from fastcfg.backoff import BackoffPolicy


BASIC_BACKOFF_POLICY = BackoffPolicy(
    max_retries=6,       # Increase the number of retries to 6
    base_delay=0.5,      # Start with a smaller base delay of 0.5 seconds
    max_delay=32,        # Keep the maximum delay at 32 seconds
    factor=2,            # Double the delay each time
    jitter=True          # Introduce jitter to reduce collision
)
