"""
Core module for Assistive AI Platform
Contains shared utilities, configuration, authentication, and rate limiting.
"""

from .geometry import (
    estimate_distance,
    get_direction,
    format_detection,
    AVG_HEIGHTS,
    DEFAULT_FOCAL_FACTOR,
    MIN_DISTANCE
)

from .config import settings
from .auth import get_current_user, create_access_token, verify_token
from .rate_limit import rate_limiter

__all__ = [
    'estimate_distance',
    'get_direction',
    'format_detection',
    'AVG_HEIGHTS',
    'DEFAULT_FOCAL_FACTOR',
    'MIN_DISTANCE',
    'settings',
    'get_current_user',
    'create_access_token',
    'verify_token',
    'rate_limiter',
]