# api/system.py
@router.get("/detect")
async def detect_system(
    current_user: User = Depends(get_current_user)
):
    """Detect system information if agent is installed"""
    try:
        # Check if agent is installed and running
        agent_response = await check_local_agent()
        
        if agent_response:
            # Agent is installed, get real data
            return await agent_response.get_system_info()
        else:
            # No agent, return basic browser detection
            return {
                "detection_method": "browser",
                "os_type": detect_os_from_user_agent(request.headers.get("User-Agent", "")),
                "requires_manual": True
            }
    except Exception as e:
        logger.error(f"System detection failed: {e}")
        return {"error": "detection_failed", "requires_manual": True}