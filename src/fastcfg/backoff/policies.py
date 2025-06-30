"""
This module defines pre-configured backoff policies for use with the exponential backoff mechanism.

Attributes:
    BASIC_BACKOFF_POLICY (BackoffPolicy): A basic backoff policy configuration 
    with the following settings:
        - max_retries: 6 (Maximum number of retry attempts)
        - base_delay: 0.5 seconds (Initial delay between retries)
        - max_delay: 32 seconds (Maximum delay between retries)
        - factor: 2 (Delay is doubled each time)
        - jitter: True (Random jitter is added to the delay to reduce collision)
"""

from fastcfg.backoff import BackoffPolicy

BASIC_BACKOFF_POLICY = BackoffPolicy(
    max_retries=6,
    base_delay=0.5,  # Start with a smaller base delay of 0.5 seconds
    max_delay=32,  # Keep the maximum delay at 32 seconds
    factor=2,  # Double the delay each time
    jitter=True,  # Introduce jitter to reduce collision
)
