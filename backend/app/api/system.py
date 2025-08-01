# api/system.py
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
import platform
import logging
from typing import Dict, Any

from app.core.auth import get_current_user
from app.models.user import User
from app.ai_agents.agent_manager import get_agent_manager

router = APIRouter()
logger = logging.getLogger("system_api")

def get_os_type() -> str:
    """Get the current operating system type."""
    system = platform.system().lower()
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
        
        # Get agent manager instance
        try:
            agent_manager = await get_agent_manager()
            if not agent_manager:
                logger.error("Failed to get agent manager instance")
                return {
                    "error": "agent_manager_unavailable",
                    "message": "Failed to initialize agent manager",
                    "requires_manual": True
                }
                
            # Get agent status
            logger.debug("Getting agent status...")
            agent_response = await agent_manager.get_agent_status()
            
            if agent_response:
                logger.debug("Agent response received, getting system info...")
                # Agent is installed, get real data
                system_info = await agent_response.get_system_info()
                logger.info("System detection successful")
                return system_info
                
        except Exception as agent_error:
            logger.exception("Error during agent-based system detection")
            # Continue to fallback if agent detection fails
        
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
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_server_error",
                "message": str(e),
                "requires_manual": True
            }
        )