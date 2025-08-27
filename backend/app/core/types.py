# from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON
import os

# Detect which database we're using
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./test.db")

# Use the appropriate JSON type
if "postgresql" in DATABASE_URL:
    PG_JSONB = JSONB
    SA_JSON = JSONB
else:
    PG_JSONB = JSON
    SA_JSON = JSON
# 
# 
# 
# 
# 
# 
# 
# """
# Shared type definitions for the application.
# """
# import json
# from typing import Any
# from sqlalchemy.types import TypeDecorator, TEXT
# from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
# from sqlalchemy.dialects.sqlite import JSON as SA_JSON

# class JSONType(TypeDecorator):
#     """
#     JSON type for storing nested dictionaries and lists in SQLite/PostgreSQL.
#     Handles the serialization/deserialization automatically.
#     """
#     impl = TEXT
#     cache_ok = True

#     def process_bind_param(self, value: Any, dialect) -> str:
#         if value is not None:
#             return json.dumps(value)
#         return None

#     def process_result_value(self, value: Any, dialect) -> dict:
#         if value is not None:
#             return json.loads(value)
#         return None

#     def load_dialect_impl(self, dialect):
#         if dialect.name == "postgresql":
#             return dialect.type_descriptor(PG_JSONB())
#         else:
#             return dialect.type_descriptor(SA_JSON())