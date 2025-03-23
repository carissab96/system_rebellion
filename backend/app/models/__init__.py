# Import all models to ensure they're registered with Base.metadata
from app.models.user import User, UserProfile
#from app.models.metrics import Metrics
#from app.models.system import System
#from app.models.alerts import Alert
# backend/app/models/__init__.py
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
