# Dell Setup Instructions - Vector DB Phase 3
**Run these commands on the Dell server**

## Step 1: Pull Latest Code
```bash
cd /path/to/system_rebellion
git pull origin distributed-mixin-implementation
```

## Step 2: Activate Virtual Environment
```bash
cd backend
source venv/bin/activate
```

## Step 3: Install Dependencies
```bash
pip install sentence-transformers
```

## Step 4: Install pgvector PostgreSQL Extension

### Option A: If you have sudo access
```bash
# For PostgreSQL 16 (adjust version if different)
sudo apt-get update
sudo apt-get install postgresql-16-pgvector
```

### Option B: Check PostgreSQL version first
```bash
psql --version
# Then install matching version, e.g.:
# sudo apt-get install postgresql-15-pgvector
# sudo apt-get install postgresql-14-pgvector
```

## Step 5: Enable pgvector in Database
```bash
# Run the setup script
python setup_pgvector.py
```

**Expected output:**
```
🔗 Connecting to database...
📦 Checking for pgvector extension...
✅ pgvector extension installed successfully!
🧪 Testing vector operations...
✅ Vector operations working!
🎉 pgvector setup complete!
```

## Step 6: Run Alembic Migration
```bash
# Apply the vector tables migration
alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade 3ea74a8cb1b5 -> 3734e17210c3, add_vector_tables_for_semantic_search
✅ Vector tables created successfully!
📊 Created 3 tables with HNSW indexes for fast semantic search
🚀 Ready for Phase 4: Dual-write implementation
```

## Step 7: Verify Tables Created
```bash
# Connect to database
psql -U carissab -d system_rebellion

# List vector tables
\dt agent_*_vectors

# Should show:
# agent_decision_vectors
# agent_pattern_vectors
# agent_interaction_vectors

# Check vector extension
\dx vector

# Exit psql
\q
```

## Troubleshooting

### If pgvector install fails:
```bash
# Check PostgreSQL version
psql --version

# Search for available pgvector packages
apt-cache search pgvector

# Install correct version
sudo apt-get install postgresql-<version>-pgvector
```

### If setup_pgvector.py fails:
- Check database connection in .env file
- Ensure PostgreSQL is running: `sudo systemctl status postgresql`
- Check database credentials

### If alembic upgrade fails:
- Check that pgvector extension is enabled: `python setup_pgvector.py`
- Check alembic version: `alembic current`
- Check for errors in migration output

## Success Checklist
- [ ] Code pulled from git
- [ ] Dependencies installed (sentence-transformers)
- [ ] pgvector extension installed on PostgreSQL
- [ ] setup_pgvector.py ran successfully
- [ ] alembic upgrade head completed
- [ ] 3 vector tables exist in database
- [ ] HNSW indexes created

## Next Steps
Once all checks pass, you're ready for **Phase 4: Dual-Write Implementation**!

The backend will start writing to both SQL and vector tables, enabling semantic search while maintaining SQL as source of truth.
