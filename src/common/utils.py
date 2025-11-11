"""
Common utilities.
"""

from datetime import datetime, date, time
from typing import Optional, Iterable, Dict, Any

import pendulum
from django.utils import timezone


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


# --- Warranty helpers -------------------------------------------------------------------------

def calculate_warranty_status(end_date: Optional[date]) -> Dict[str, Any]:
    """
    計算保固狀態，回傳 state/label/days_left/color。
    - state: none | active | expiring | expired
    - color: success | warning | danger | gray
    """
    if not end_date:
        return {
            'state': 'none',
            'label': '無保固',
            'days_left': None,
            'color': 'gray',
        }

    if isinstance(end_date, datetime):
        end_date = end_date.date()

    today = timezone.localdate()
    days_left = (end_date - today).days

    if days_left < 0:
        return {
            'state': 'expired',
            'label': '已過保',
            'days_left': abs(days_left),
            'color': 'danger',
        }

    if days_left <= 15:
        return {
            'state': 'expiring',
            'label': f'即將到期 (剩 {days_left} 天)',
            'days_left': days_left,
            'color': 'warning',
        }

    return {
        'state': 'active',
        'label': f'保固中 (剩 {days_left} 天)',
        'days_left': days_left,
        'color': 'success',
    }


def summarize_warranties(warranties: Iterable) -> Dict[str, Any]:
    """
    將客戶的保固批次整理成摘要資訊。
    傳入 queryset/list，元素需具有 `end_date`、`title`、`id`。
    """
    warranties = [w for w in warranties if getattr(w, 'end_date', None)]
    if not warranties:
        return {
            'count': 0,
            'next_id': None,
            'next_title': None,
            'next_due_date': None,
            'status': calculate_warranty_status(None),
        }

    warranties.sort(key=lambda w: w.end_date or date.max)
    next_warranty = warranties[0]
    status = calculate_warranty_status(next_warranty.end_date)

    return {
        'count': len(warranties),
        'next_id': next_warranty.id,
        'next_title': next_warranty.title,
        'next_due_date': next_warranty.end_date,
        'status': status,
    }


def warranty_date_to_datetime(value: Optional[date]) -> Optional[datetime]:
    """將 Date 轉換為當地時區的 DateTime（兼容舊欄位使用）。"""
    if not value:
        return None

    if isinstance(value, datetime):
        return value

    tz = timezone.get_current_timezone()
    dt = datetime.combine(value, time.min)
    return timezone.make_aware(dt, tz)

