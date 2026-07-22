"""
╔══════════════════════════════════════════════════════════════╗
║              HANDLERS - aiogram 2.x                          ║
╚══════════════════════════════════════════════════════════════╝
"""

from .start_handler import router as start_router
from .verification_handler import router as verification_router
from .admin_handler import router as admin_router
from .panel_handler import router as panel_router
from .group_handler import router as group_router

__all__ = [
    'start_router',
    'verification_router', 
    'admin_router',
    'panel_router',
    'group_router'
]
