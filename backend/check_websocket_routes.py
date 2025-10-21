"""
Quick diagnostic to check if WebSocket routes are registered
"""
import sys
sys.path.insert(0, '.')

from app.api import agent_events_websocket, agent_insights_websocket

print("="*60)
print("WEBSOCKET ROUTE DIAGNOSTIC")
print("="*60)

print("\n1. Agent Events WebSocket:")
print(f"   Module: {agent_events_websocket}")
print(f"   Has router: {hasattr(agent_events_websocket, 'router')}")
if hasattr(agent_events_websocket, 'router'):
    print(f"   Router: {agent_events_websocket.router}")
    print(f"   Routes: {agent_events_websocket.router.routes}")

print("\n2. Agent Insights WebSocket:")
print(f"   Module: {agent_insights_websocket}")
print(f"   Has router: {hasattr(agent_insights_websocket, 'router')}")
if hasattr(agent_insights_websocket, 'router'):
    print(f"   Router: {agent_insights_websocket.router}")
    print(f"   Routes: {agent_insights_websocket.router.routes}")

print("\n" + "="*60)
