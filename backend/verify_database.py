# verify_database.py
from sqlalchemy import create_engine, inspect
from app.core.database import Base

# Create engine
engine = create_engine('sqlite:///./system_rebellion.db')

# Create inspector
inspector = inspect(engine)

# List tables
print("Tables in database:")
for table_name in inspector.get_table_names():
    print(f"- {table_name}")
    
    # Show columns for each table
    print("  Columns:")
    for column in inspector.get_columns(table_name):
        print(f"  - {column['name']}: {column['type']}")