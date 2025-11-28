#!/usr/bin/env python3
"""
Add vector writes to all agent database integrations
This script adds the import statements needed for vector writes
"""

import os
import re

# Agent database integration files
AGENT_FILES = [
    "backend/app/ai_agents/meth_snail/database_integration.py",
    "backend/app/ai_agents/hamsters/hamsters_database_integration.py",
    "backend/app/ai_agents/the_stick/database_integration.py",
    "backend/app/ai_agents/quantum_shadow_people/database_integration.py",
]

IMPORT_BLOCK = """from app.services.embedding_service import get_embedding_service, create_decision_text
from app.services.vector_storage import get_vector_storage"""

def add_imports_to_file(filepath):
    """Add vector service imports to a file if not already present"""
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if imports already exist
    if 'from app.services.embedding_service import' in content:
        print(f"✅ {filepath} - imports already present")
        return True
    
    # Find a good place to add imports (after other app imports)
    # Look for "from app." imports
    app_import_pattern = r'(from app\.[^\n]+\n)(?!from app\.)'
    
    matches = list(re.finditer(app_import_pattern, content))
    if matches:
        # Insert after the last app import
        last_match = matches[-1]
        insert_pos = last_match.end()
        
        new_content = (
            content[:insert_pos] +
            IMPORT_BLOCK + "\n" +
            content[insert_pos:]
        )
        
        with open(filepath, 'w') as f:
            f.write(new_content)
        
        print(f"✅ {filepath} - imports added")
        return True
    else:
        print(f"⚠️  {filepath} - couldn't find insertion point")
        return False

def main():
    print("🔮 Adding vector service imports to all agents...")
    print()
    
    success_count = 0
    for filepath in AGENT_FILES:
        if add_imports_to_file(filepath):
            success_count += 1
    
    print()
    print(f"✅ Added imports to {success_count}/{len(AGENT_FILES)} files")
    print()
    print("⚠️  MANUAL STEP REQUIRED:")
    print("   You need to add the actual vector write code after each")
    print("   'await session.commit()' in each agent's decision storage methods.")
    print()
    print("   Pattern to add:")
    print("   ```python")
    print("   # === WRITE 3: VECTOR EMBEDDING (NON-BLOCKING) ===")
    print("   try:")
    print("       decision_text = create_decision_text(...)")
    print("       embedding_service = get_embedding_service()")
    print("       embedding = await embedding_service.generate_embedding_async(decision_text)")
    print("       vector_storage = get_vector_storage()")
    print("       vector_storage.store_decision_vector_fire_and_forget(...)")
    print("       logger.debug(f'🔮 Queued vector embedding for decision {memory_id}')")
    print("   except Exception as ve:")
    print("       logger.warning(f'⚠️ Vector embedding failed (non-critical): {ve}')")
    print("   ```")

if __name__ == "__main__":
    main()
