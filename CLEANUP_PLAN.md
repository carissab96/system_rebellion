# SYSTEM REBELLION - CLEANUP & REORGANIZATION PLAN

**Date**: November 13, 2025  
**Objective**: Clean, organized, professional file structure for world-class documentation

---

## BACKEND CLEANUP

### Current Issues:
- Tests scattered: `/backend/tests/`, `/backend/dev-tools/tests/`, root-level test files
- Docs scattered: `/backend/markdown_docs/`, `/backend/docs/`, `/backend/scripts/`
- Scripts in multiple places: `/backend/scripts/`, `/backend/dev-tools/scripts/`
- Root-level test files polluting main directory

### New Structure:
```
backend/
├── app/                          # Application code (keep as-is)
├── tests/                        # ALL tests consolidated here
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── distributed/              # Distributed agent tests
├── docs/                         # ALL documentation
│   ├── architecture/             # Architecture docs
│   ├── implementation/           # Implementation guides
│   ├── api/                      # API documentation
│   └── guides/                   # User guides
├── scripts/                      # Production scripts only
│   ├── migration/                # Database migrations
│   └── deployment/               # Deployment scripts
├── dev-tools/                    # Development tools
│   ├── debug/                    # Debug utilities
│   └── analysis/                 # Code analysis tools
├── alembic/                      # Database migrations (keep)
└── [config files]                # Root config files
```

### Actions:

**1. Consolidate Tests**
- Move `/backend/dev-tools/tests/TESTS/*` → `/backend/tests/unit/`
- Move root-level `test_*.py` → `/backend/tests/integration/`
- Keep current `/backend/tests/test_distributed_*.py` → `/backend/tests/distributed/`
- Delete empty test directories

**2. Consolidate Documentation**
- Move `/backend/markdown_docs/*` → `/backend/docs/`
- Organize by category (architecture, implementation, guides)
- Remove duplicate/outdated docs
- Keep only origin story legacy docs

**3. Consolidate Scripts**
- Move introspection scripts → `/backend/dev-tools/analysis/`
- Keep migration scripts in `/backend/scripts/migration/`
- Remove redundant scripts

**4. Remove Legacy/Unused**
- Delete: `psutil_freeze.json`, `psutil_snapshot.json` (snapshots, not needed)
- Delete: `dump.rdb` (Redis dump, regenerates)
- Delete: Empty markdown files
- Delete: Duplicate config directories

---

## FRONTEND CLEANUP

### Current Issues:
- Tests in `src/__tests__/` (should be colocated or in root `/tests/`)
- Multiple config directories: `src/config/`, `src/frontend-config/`
- Redundant type definitions

### New Structure:
```
frontend/
├── src/
│   ├── components/               # Keep organized
│   ├── pages/                    # Keep organized
│   ├── services/                 # API & WebSocket services
│   ├── store/                    # Redux store
│   ├── types/                    # TypeScript types (consolidated)
│   ├── hooks/                    # Custom hooks
│   ├── styles/                   # Global styles
│   └── config/                   # Single config directory
├── tests/                        # Move tests here
│   ├── unit/
│   └── integration/
└── [config files]
```

### Actions:

**1. Consolidate Tests**
- Move `src/__tests__/*` → `/frontend/tests/`
- Organize by type (unit, integration)

**2. Consolidate Config**
- Merge `src/config/` and `src/frontend-config/`
- Single source of truth

**3. Clean Types**
- Review and consolidate type definitions
- Remove duplicates

---

## FILES TO DELETE

### Backend:
- `test_agent_resurrection.py` (root level)
- `test_distributed_agents.py` (root level)
- `test_distributed_agents_standalone.py` (root level)
- `test_distributed_config.py` (root level)
- `psutil_freeze.json`
- `psutil_snapshot.json`
- `dump.rdb`
- Empty markdown files in `/backend/markdown_docs/`

### Frontend:
- Duplicate config files
- Unused component files (TBD after review)

---

## EXECUTION ORDER

1. **Backend Tests** - Consolidate all tests
2. **Backend Docs** - Organize documentation
3. **Backend Scripts** - Clean up scripts
4. **Backend Cleanup** - Remove legacy files
5. **Frontend Tests** - Move and organize
6. **Frontend Config** - Consolidate configs
7. **Final Verification** - Ensure nothing broke

---

## SUCCESS CRITERIA

✅ All tests in organized `/tests/` directories  
✅ All docs in organized `/docs/` directory  
✅ No duplicate files  
✅ No legacy/unused files  
✅ Clear, professional structure  
✅ All tests still pass  
✅ Documentation is discoverable  

---

**LET'S MAKE THIS REBELLION LOOK PROFESSIONAL!** 🔥
