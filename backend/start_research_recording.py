#!/usr/bin/env python3
"""
Start Research Recording
========================

Starts the event logger and behavior tracker for documenting emergent AI behavior.

Usage:
    python start_research_recording.py

This will:
1. Initialize the event logger
2. Start the behavior tracker
3. Print real-time statistics
4. Save session data on exit

Press Ctrl+C to stop recording and save data.
"""

import asyncio
import signal
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.ai_agents.distributed.event_logger import get_event_logger
from app.ai_agents.distributed.behavior_tracker import get_behavior_tracker


class ResearchRecorder:
    """Manages research recording session"""
    
    def __init__(self):
        self.logger = get_event_logger()
        self.tracker = get_behavior_tracker()
        self.running = False
        
    async def start(self, snapshot_interval: float = 2.0):
        """Start recording"""
        print("\n" + "="*60)
        print("🎥 RESEARCH RECORDING STARTED")
        print("="*60)
        print(f"Session ID: {self.logger.session_id}")
        print(f"Event Log: {self.logger.current_log_file}")
        print(f"Snapshot Interval: {snapshot_interval}s")
        print("\nPress Ctrl+C to stop recording and save data\n")
        print("="*60 + "\n")
        
        # Start behavior tracker
        await self.tracker.start(snapshot_interval=snapshot_interval)
        
        self.running = True
        
        # Print statistics every 30 seconds
        try:
            while self.running:
                await asyncio.sleep(30)
                self.print_stats()
        except KeyboardInterrupt:
            await self.stop()
    
    async def stop(self):
        """Stop recording and save data"""
        print("\n" + "="*60)
        print("⏹️  STOPPING RECORDING...")
        print("="*60 + "\n")
        
        self.running = False
        
        # Stop tracker
        await self.tracker.stop()
        
        # Save summaries
        await self.logger.save_session_summary()
        await self.tracker.save_patterns()
        
        # Print final statistics
        print("\n" + "="*60)
        print("📊 FINAL SESSION STATISTICS")
        print("="*60)
        self.logger.print_statistics()
        
        tracker_stats = self.tracker.get_statistics()
        print("\n🔍 Behavior Tracker Statistics:")
        print(f"  Total Snapshots: {tracker_stats['total_snapshots']}")
        print(f"  Formations Detected: {tracker_stats['formations_detected']}")
        print(f"  Patterns Detected: {tracker_stats['patterns_detected']}")
        print(f"  Active Agents: {tracker_stats['active_agents']}")
        print(f"  Communication Links: {tracker_stats['communication_links']}")
        
        print("\n" + "="*60)
        print("💾 SESSION DATA SAVED")
        print("="*60)
        print(f"Event Log: {self.logger.current_log_file}")
        print(f"Summary: {self.logger.summary_file}")
        print(f"Snapshots: {self.tracker.snapshot_file}")
        print(f"Patterns: {self.tracker.patterns_file}")
        print("\n🌟 Research data captured successfully!")
        print("="*60 + "\n")
    
    def print_stats(self):
        """Print current statistics"""
        print("\n" + "-"*60)
        print(f"📊 Statistics Update - {self.logger.session_id}")
        print("-"*60)
        
        summary = self.logger.get_session_summary()
        print(f"Total Events: {summary['total_events']}")
        print(f"Emergent Events: {summary['emergent_events_count']}")
        print(f"Duration: {summary['duration_seconds']:.1f}s")
        
        tracker_stats = self.tracker.get_statistics()
        print(f"Formations Detected: {tracker_stats['formations_detected']}")
        print(f"Patterns Detected: {tracker_stats['patterns_detected']}")
        print("-"*60 + "\n")


async def main():
    """Main entry point"""
    recorder = ResearchRecorder()
    
    # Setup signal handlers
    def signal_handler(sig, frame):
        print("\n\n🛑 Interrupt received...")
        asyncio.create_task(recorder.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start recording
    await recorder.start(snapshot_interval=2.0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n✅ Recording stopped")
        sys.exit(0)
