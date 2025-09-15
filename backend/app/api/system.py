# api/system.py
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
import platform
import logging
from typing import Dict, Any

from app.core.config import get_settings
s=get_settings()
from app.core.auth import get_current_user
from app.models.user import User
from app.ai_agents.agent_manager import get_agent_manager

router = APIRouter()
logger = logging.getLogger("system_api")

def get_os_type() -> str:
    """Get the current operating system type."""
    system = platform.system().lower()
        
    # Basic OS detection that works in most environments
    if system == 'darwin':
        return 'darwin'
    elif system == 'linux':
        return 'linux'
    elif system == 'windows':
        return 'windows'
    return 'unknown'

@router.get("/detect")
async def detect_system(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Detect system information if agent is installed.
        
    Returns:
        Dict containing system information or error details
    """
    try:
        logger.info("Starting system detection for user: %s", current_user.email)
        
        # Try to get agent manager and system info
        try:
            agent_manager = await get_agent_manager()
            logger.debug("Getting agent status...")
            agent_response = await agent_manager.get_agent_status()
                
            if agent_response:
                logger.debug("Agent response received, getting system info...")
                system_info = await agent_response.get_system_info()
                logger.info("System detection successful")
                return system_info
                
        except Exception as agent_error:
            logger.exception("Error during agent-based system detection")
            # Fall through to fallback detection below
        
        # Fallback to basic system detection
        logger.info("Using fallback system detection")
        return {
            "detection_method": "platform",
            "os_type": get_os_type(),
            "requires_manual": True,
            "fallback_reason": "agent_unavailable"
        }
        
    except Exception as e:
        logger.exception("Unexpected error in detect_system endpoint")
        return {
            "error": "internal_server_error",
            "message": str(e),
            "requires_manual": True
        }