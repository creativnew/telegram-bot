"""
╔══════════════════════════════════════════════════════════════╗
║              MIDDLEWARES - aiogram 2.x                         ║
╚══════════════════════════════════════════════════════════════╝
"""

from .group_middleware import setup_middleware as setup_group_middleware
from .admin_middleware import setup_middleware as setup_admin_middleware

__all__ = ['setup_group_middleware', 'setup_admin_middleware']
