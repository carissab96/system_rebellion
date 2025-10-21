# backend/workers/db_processor.py
import asyncio
async def process_memory_batch(memory_service, batch_size=50):
    """Process queued memories in batches"""
    while True:
        try:
            # Ensure memory service is ready
            await memory_service.ensure_ready()
            
            tasks = await memory_service.task_queue.dequeue(batch_size)
            
            if tasks:
                # Batch process similar operations
                memories_to_store = [t['data'] for t in tasks if t['type'] == 'memory_store']
                
                if memories_to_store:
                    # Process each memory (they will use the existing session)
                    for mem in memories_to_store:
                        try:
                            await memory_service._direct_store(**mem)
                        except Exception as mem_error:
                            print(f"Failed to store memory: {mem_error}")
                            
                print(f"Processed {len(tasks)} tasks")
                
            else:
                await asyncio.sleep(1)  # No tasks, wait
                
        except Exception as e:
            print(f"Batch processor error: {e}")
            await asyncio.sleep(5)