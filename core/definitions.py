"""Definitions."""

import os
from pathlib import Path

ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
"""Root directory."""

AUTH_REQUIRED = '__auth_required__'
"""Auth required indicator."""

USE_ODATA = '__use_odata__'
"""OData V4 query indicator."""
