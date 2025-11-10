"""
Common utilities.
"""

import pendulum
from typing import Optional


def parse_datetime(value: str) -> Optional[pendulum.DateTime]:
    """Parse datetime string to pendulum.DateTime."""
    if not value:
        return None
    try:
        return pendulum.parse(value)
    except Exception:
        return None


def format_datetime(dt: Optional[pendulum.DateTime], format_str: str = 'YYYY-MM-DD HH:mm:ss') -> str:
    """Format pendulum.DateTime to string."""
    if not dt:
        return ''
    return dt.format(format_str)

