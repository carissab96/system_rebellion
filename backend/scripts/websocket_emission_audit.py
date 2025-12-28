#!/usr/bin/env python3
"""
WebSocket Emission Audit Script
Captures and logs ALL backend-to-frontend WebSocket emissions with source tracking.

This script connects to the backend WebSocket and captures:
1. Direct WebSocket broadcasts (agent_decision, agent_insight, agent_event, etc.)
2. Redis pub/sub forwarding (agents:broadcast, triage:decisions, etc.)
3. Agent logs (via WebSocketLogHandler)
4. System metrics and heartbeats

Output: Detailed log file with message types, sources, and full payloads
"""

import asyncio
import websockets
import json
from datetime import datetime
from collections import defaultdict
from typing import Dict, Any, Set
import sys

# Message type tracking
message_counts: Dict[str, int] = defaultdict(int)
message_sources: Dict[str, Set[str]] = defaultdict(set)
all_messages = []

# Known message types from codebase analysis
KNOWN_MESSAGE_TYPES = {
    # Direct WebSocket broadcasts
    "agent_decision": "agent_decision_emitter.py - Full ML pipeline (perception→reasoning→action→learning)",
    "agent_insight": "agent_insight_emitter.py - Inter-agent communication and reasoning",
    "agent_event": "agent_event_logger.py - Agent lifecycle events",
    "agent_log": "websocket_log_handler.py - Python logging output from agents",
    "agent_memory_update": "agent_insight_emitter.py - Memory bank updates",
    "personality_behavior": "agent_decision_emitter.py - Personality behaviors (shell spins, energy drinks, etc.)",
    
    # Redis pub/sub forwarding (via WebSocketManager)
    "triage_decision": "Redis: agents:decisions, triage:decisions → websockets.py",
    "resource_alert": "Redis: agents:resources:alerts, resource:alerts → websockets.py",
    "emergency": "Redis: agents:emergency → websockets.py",
    "agent_heartbeat": "Redis: agents:heartbeats → websockets.py",
    "learning_update": "Redis: agents:learning → websockets.py",
    "coordination_request": "Redis: coordination:requests → websockets.py",
    "agent_action": "Redis: agent:actions → websockets.py",
    "agent_message": "Redis: agents:broadcast, agent:broadcast → websockets.py",
    
    # System messages
    "heartbeat": "websockets.py - WebSocket keepalive (every 30s)",
    "agent_roster": "simplified_websocket_routes.py - Active agent list",
    "system_metrics": "Metrics service broadcasts",
}

# Redis channels being monitored
REDIS_CHANNELS = [
    'agents:broadcast',
    'agents:decisions',
    'agents:resources:alerts',
    'agents:emergency',
    'agents:heartbeats',
    'agents:learning',
    'agent:broadcast',
    'triage:decisions',
    'resource:alerts',
    'coordination:requests',
    'agent:actions',
]


def format_timestamp():
    """Get formatted timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def log_message(msg: str, file_handle):
    """Log to both console and file"""
    timestamped = f"[{format_timestamp()}] {msg}"
    print(timestamped)
    file_handle.write(timestamped + "\n")
    file_handle.flush()


def analyze_message(data: Dict[str, Any], log_file) -> None:
    """Analyze and categorize a WebSocket message"""
    msg_type = data.get("type", "unknown")
    message_counts[msg_type] += 1
    
    # Track source information
    source_info = []
    
    # Determine source based on message structure
    if msg_type == "agent_decision":
        agent_name = data.get("agent_name", "unknown")
        source_info.append(f"Agent: {agent_name}")
        source_info.append(f"Source: distributed_{agent_name}.py → agent_decision_emitter.py")
        message_sources[msg_type].add(agent_name)
        
    elif msg_type == "agent_insight":
        from_agent = data.get("from_agent", "unknown")
        to_agent = data.get("to_agent", "unknown")
        action = data.get("action", "unknown")
        source_info.append(f"From: {from_agent} → To: {to_agent}")
        source_info.append(f"Action: {action}")
        source_info.append("Source: agent_insight_emitter.py")
        message_sources[msg_type].add(f"{from_agent}→{to_agent}")
        
    elif msg_type == "agent_log":
        agent_name = data.get("agent_name", "unknown")
        category = data.get("category", "unknown")
        logger = data.get("logger", "unknown")
        source_info.append(f"Agent: {agent_name}")
        source_info.append(f"Category: {category}")
        source_info.append(f"Logger: {logger}")
        source_info.append("Source: websocket_log_handler.py")
        message_sources[msg_type].add(f"{agent_name}/{category}")
        
    elif msg_type == "agent_event":
        agent_name = data.get("agent_name", "unknown")
        event_type = data.get("event_type", "unknown")
        source_info.append(f"Agent: {agent_name}")
        source_info.append(f"Event: {event_type}")
        source_info.append("Source: agent_event_logger.py")
        message_sources[msg_type].add(f"{agent_name}/{event_type}")
        
    elif msg_type == "personality_behavior":
        agent_name = data.get("agent_name", "unknown")
        behavior_type = data.get("behavior_type", "unknown")
        source_info.append(f"Agent: {agent_name}")
        source_info.append(f"Behavior: {behavior_type}")
        source_info.append("Source: agent_decision_emitter.py")
        message_sources[msg_type].add(f"{agent_name}/{behavior_type}")
        
    elif "redis_channel" in data:
        # Message forwarded from Redis
        channel = data.get("redis_channel", "unknown")
        source_info.append(f"Redis Channel: {channel}")
        source_info.append("Source: websockets.py → Redis pub/sub bridge")
        message_sources[msg_type].add(f"redis:{channel}")
        
    else:
        source_info.append(f"Source: {KNOWN_MESSAGE_TYPES.get(msg_type, 'Unknown source')}")
    
    # Log the message
    log_message("=" * 80, log_file)
    log_message(f"MESSAGE TYPE: {msg_type} (#{message_counts[msg_type]})", log_file)
    for info in source_info:
        log_message(f"  {info}", log_file)
    log_message(f"\nFULL PAYLOAD:", log_file)
    log_message(json.dumps(data, indent=2), log_file)
    log_message("=" * 80 + "\n", log_file)
    
    # Store for summary
    all_messages.append({
        "timestamp": format_timestamp(),
        "type": msg_type,
        "source_info": source_info,
        "payload": data
    })


def print_summary(log_file):
    """Print summary statistics"""
    log_message("\n" + "=" * 80, log_file)
    log_message("WEBSOCKET EMISSION AUDIT SUMMARY", log_file)
    log_message("=" * 80, log_file)
    
    log_message(f"\nTotal messages captured: {sum(message_counts.values())}", log_file)
    log_message(f"Unique message types: {len(message_counts)}", log_file)
    
    log_message("\n--- MESSAGE TYPE BREAKDOWN ---", log_file)
    for msg_type, count in sorted(message_counts.items(), key=lambda x: x[1], reverse=True):
        log_message(f"  {msg_type}: {count} messages", log_file)
        if msg_type in KNOWN_MESSAGE_TYPES:
            log_message(f"    → {KNOWN_MESSAGE_TYPES[msg_type]}", log_file)
        if msg_type in message_sources and message_sources[msg_type]:
            sources = ", ".join(sorted(message_sources[msg_type]))
            log_message(f"    → Sources: {sources}", log_file)
    
    log_message("\n--- BACKEND SOURCE FILES ---", log_file)
    log_message("Direct WebSocket Broadcasts:", log_file)
    log_message("  • agent_decision_emitter.py - emit_agent_decision(), emit_personality_behavior()", log_file)
    log_message("  • agent_insight_emitter.py - emit_agent_insight(), emit_coordination_insight(), etc.", log_file)
    log_message("  • agent_event_logger.py - emit_agent_event()", log_file)
    log_message("  • websocket_log_handler.py - WebSocketLogHandler.emit()", log_file)
    
    log_message("\nRedis Pub/Sub → WebSocket Bridge:", log_file)
    log_message("  • websockets.py - WebSocketManager._subscribe_to_agent_messages()", log_file)
    log_message("  • Channels monitored:", log_file)
    for channel in REDIS_CHANNELS:
        log_message(f"    - {channel}", log_file)
    
    log_message("\nAgent Emission Points:", log_file)
    log_message("  • distributed_meth_snail.py (~line 340)", log_file)
    log_message("  • distributed_hamsters.py (~line 340)", log_file)
    log_message("  • distributed_qsp.py (~line 273)", log_file)
    log_message("  • distributed_hawkington.py (~line 441)", log_file)
    log_message("  • distributed_vic20.py (~line 373)", log_file)
    log_message("  • distributed_stick.py (~line 280)", log_file)
    
    log_message("\n--- UNKNOWN MESSAGE TYPES ---", log_file)
    unknown_types = [t for t in message_counts.keys() if t not in KNOWN_MESSAGE_TYPES]
    if unknown_types:
        for msg_type in unknown_types:
            log_message(f"  ⚠️  {msg_type} - NOT DOCUMENTED", log_file)
    else:
        log_message("  ✅ All message types are documented", log_file)
    
    log_message("\n" + "=" * 80, log_file)


async def monitor_websocket(uri: str, duration: int, output_file: str):
    """Monitor WebSocket for specified duration"""
    
    # Ensure output directory exists
    import os
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as log_file:
        log_message(f"🔌 WebSocket Emission Audit", log_file)
        log_message(f"Connecting to: {uri}", log_file)
        log_message(f"Duration: {duration} seconds", log_file)
        log_message(f"Output: {output_file}", log_file)
        log_message("=" * 80 + "\n", log_file)
        
        try:
            async with websockets.connect(uri) as websocket:
                log_message("✅ Connected successfully!", log_file)
                log_message("⏳ Monitoring WebSocket emissions...\n", log_file)
                
                start_time = asyncio.get_event_loop().time()
                
                while True:
                    try:
                        # Check if duration exceeded
                        elapsed = asyncio.get_event_loop().time() - start_time
                        if elapsed >= duration:
                            log_message(f"\n⏱️  Duration {duration}s reached", log_file)
                            break
                        
                        # Wait for message with timeout
                        remaining = duration - elapsed
                        message = await asyncio.wait_for(
                            websocket.recv(),
                            timeout=min(remaining, 5.0)
                        )
                        
                        # Parse and analyze
                        data = json.loads(message)
                        analyze_message(data, log_file)
                        
                    except asyncio.TimeoutError:
                        # No message in timeout period, continue
                        continue
                    except json.JSONDecodeError as e:
                        log_message(f"❌ JSON decode error: {e}", log_file)
                        log_message(f"   Raw message: {message[:200]}", log_file)
                    except Exception as e:
                        log_message(f"❌ Error processing message: {e}", log_file)
                
                # Print summary
                print_summary(log_file)
                
        except websockets.exceptions.InvalidStatusCode as e:
            log_message(f"❌ Invalid status code: {e}", log_file)
            log_message("   This might mean authentication is required", log_file)
        except Exception as e:
            log_message(f"❌ Connection error: {e}", log_file)
            import traceback
            log_message(traceback.format_exc(), log_file)


def main():
    """Main entry point"""
    # Configuration
    backend_host = "localhost"  # Change to 192.168.1.127 if running from HP
    backend_port = 8000
    uri = f"ws://{backend_host}:{backend_port}/api/ws/system-metrics"
    
    # Duration in seconds (default: 5 minutes)
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    
    # Output file - use relative path from script location
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(script_dir, "..", "logs")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(logs_dir, f"websocket_audit_{timestamp}.log")
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    WebSocket Emission Audit Script                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

This script captures ALL backend-to-frontend WebSocket emissions:

📡 DIRECT BROADCASTS:
   • agent_decision - Full ML pipeline (perception→reasoning→action→learning)
   • agent_insight - Inter-agent communication and reasoning
   • agent_event - Agent lifecycle events
   • agent_log - Python logging output from agents
   • personality_behavior - Shell spins, energy drinks, beer, duct tape, etc.
   • agent_memory_update - Memory bank updates

🌉 REDIS PUB/SUB BRIDGE:
   • triage_decision, resource_alert, emergency
   • agent_heartbeat, learning_update, coordination_request
   • agent_action, agent_message

📊 SYSTEM MESSAGES:
   • heartbeat - WebSocket keepalive
   • agent_roster - Active agent list
   • system_metrics - Metrics broadcasts

Configuration:
  URI: {uri}
  Duration: {duration} seconds
  Output: {output_file}

Press Ctrl+C to stop early...
""")
    
    try:
        asyncio.run(monitor_websocket(uri, duration, output_file))
        print(f"\n✅ Audit complete! Results saved to: {output_file}")
    except KeyboardInterrupt:
        print("\n⏹️  Stopped by user")
        print(f"Partial results saved to: {output_file}")


if __name__ == "__main__":
    main()
