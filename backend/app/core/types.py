"""
Shared type definitions for the application.
"""
import json
from typing import Any
from sqlalchemy.types import TypeDecorator, TEXT
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
from sqlalchemy.dialects.sqlite import JSON as SA_JSON

class JSONType(TypeDecorator):
    """
    JSON type for storing nested dictionaries and lists in SQLite/PostgreSQL.
    Handles the serialization/deserialization automatically.
    """
    impl = TEXT, SA_JSON, PG_JSONB
    cache_ok = True

    def process_bind_param(self, value: Any, dialect) -> str:
        if value is not None:
            return json.dumps(value)
        return None

    def process_result_value(self, value: Any, dialect) -> dict:
        if value is not None:
            return json.loads(value)
        return None

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_JSONB())
        else:
            return dialect.type_descriptor(SA_JSON())