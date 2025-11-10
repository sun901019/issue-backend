"""
Local development settings.
"""

from .base import *

DEBUG = True

# 開發環境允許所有來源（僅開發用）
CORS_ALLOW_ALL_ORIGINS = True

# 開發環境關閉認證（可選）
REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = [
    'rest_framework.permissions.AllowAny',
]

