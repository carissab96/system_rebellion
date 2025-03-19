from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.middlware import setup_middleware
from app.api.endpoints.csrf import router as csrf_routes
from app.api.endpoints import auth, metrics, optimization, system, user, project, task, job, alert, configuration

def create_application() -> FastAPI:
    # Create FastAPI app
    app = FastAPI(
        title="System Rebellion",
        description="Quantum Optimization Platform",
        version="0.1.0"
    )
    
    # Setup middleware
    setup_middleware(app)
    
    # Include routers
    app.include_router(
        csrf_routes.router, 
        prefix="/api/csrf", 
        tags=["CSRF"]
    )
    app.include_router(
        auth.router, 
        prefix="/api/auth", 
        tags=["Authentication"]
    )
    # Add other routers...

    return app

# Create the app
app = create_application()
sqlalchemy.url = sqlite:///./system_rebellion.db
# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "X-CSRFToken"],
)

@app.get("/api/csrf-token")
async def get_csrf_token(request: Request):
    csrf = CSRFProtection()
    token = csrf.generate_csrf_token(request)
    return {"csrf_token": token}

@app.post("/api/protected-route")
async def protected_route(request: Request):
    csrf = CSRFProtection()
    csrf.validate_csrf_token(request)
    return {"message": "CSRF token is valid"}

# Include API endpoints
app.include_router(websockets.router)

# Include authentication endpoints
app.include_router(auth.router)

# Include optimization endpoints
app.include_router(optimization.router)

# Include metrics endpoints
app.include_router(metrics.router)

# Include system endpoints
app.include_router(system.router)

# Include user endpoints
app.include_router(user.router)

# Include project endpoints
app.include_router(project.router)

# Include task endpoints
app.include_router(task.router)

# Include job endpoints
app.include_router(job.router)

# Include alert endpoints
app.include_router(alert.router)

# Include configuration endpoints
app.include_router(configuration.router)
