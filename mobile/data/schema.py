"""
Re-export schema from data.db.schema to keep a single source of truth.
"""

from data.db.schema import SCHEMA_SQL, SCHEMA_VERSION

__all__ = ["SCHEMA_SQL", "SCHEMA_VERSION"]
