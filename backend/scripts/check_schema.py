from sqlalchemy import create_engine, inspect

def check_schema():
    # Connect to the SQLite database
    engine = create_engine('sqlite:///system_rebellion.db')
    inspector = inspect(engine)
    
    # Check if agent_memories table exists
    if 'agent_memories' in inspector.get_table_names():
        print("\nAgent Memories Table Schema:")
        print("-" * 80)
        for column in inspector.get_columns('agent_memories'):
            print(f"{column['name']}: {column['type']} (Primary Key: {column.get('primary_key', False)})")
        
        print("\nForeign Keys:")
        for fk in inspector.get_foreign_keys('agent_memories'):
            print(f"- {fk['name']}: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    else:
        print("agent_memories table does not exist")
    
    # Check alembic_version table
    if 'alembic_version' in inspector.get_table_names():
        print("\nAlembic Version:")
        with engine.connect() as conn:
            result = conn.execute("SELECT * FROM alembic_version").fetchone()
            print(f"Current version: {result[0] if result else 'No version found'}")
    else:
        print("\nAlembic version table does not exist")

if __name__ == "__main__":
    check_schema()
