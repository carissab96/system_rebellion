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

## Step 3: Install Dependencies (CPU-Only, No CUDA Bloat)

**IMPORTANT:** We're doing CPU inference only. Skip the massive NVIDIA CUDA downloads.

```bash
# Install PyTorch CPU-only first (way smaller, way faster)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Then install sentence-transformers (will use CPU torch)
pip install sentence-transformers
```

**Why CPU-only?**
- Embedding generation is ~38ms on CPU (fast enough)
- CUDA packages are 2-3GB+ of bloat we don't need
- We're not training models, just doing inference
- Saves hours of download time and GBs of disk space

**If you already started the full install:**
```bash
# Kill it and start over
Ctrl+C

# Uninstall the bloat
pip uninstall torch torchvision torchaudio -y

# Install CPU-only version
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers
```

## Step 4: Install pgvector PostgreSQL Extension

### For Arch Linux (btw)
```bash
# Check PostgreSQL version
psql --version

# Install pgvector from AUR
yay -S pgvector
# OR
paru -S pgvector

# If you don't have an AUR helper, manual install:
git clone https://aur.archlinux.org/pgvector.git
cd pgvector
makepkg -si
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

### If pgvector install fails (Arch):
```bash
# Check PostgreSQL version
psql --version

# Search AUR for pgvector
yay -Ss pgvector
# or
paru -Ss pgvector

# Check if PostgreSQL is running
sudo systemctl status postgresql

# If pgvector build fails, install build dependencies
sudo pacman -S base-devel postgresql-libs
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
