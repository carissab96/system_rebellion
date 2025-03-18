# core/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
import psutil
import logging
import sys
from datetime import datetime
from asgiref.sync import sync_to_async
from app.optimization.web_auto_tuner import WebAutoTuner

# Configure logging to output to console
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class MetricsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info("=== WEBSOCKET CONNECTION ATTEMPT DETECTED ===")
        logger.info(f"🔍 Connection ID: {id(self)}")
        logger.info(f"🔍 Connection Path: {self.scope['path']}")
        logger.info(f"🔍 Connection Headers: {dict(self.scope['headers'])}")
        
        try:
            await self.accept()
            logger.info("✅ CONNECTION SUCCESSFULLY ACCEPTED!")
            asyncio.create_task(self.send_metrics())
        except Exception as e:
            logger.error(f"❌ CONNECTION ACCEPTANCE FAILED: {str(e)}")
            logger.exception("Detailed traceback:")
    async def send_metrics(self):
        print(f"📊 Starting metrics stream for connection {id(self)}")
        try:
            while True:
                metrics = {
                    "type": "metrics_update",
                    "data": {
                        "cpu": psutil.cpu_percent(interval=1),
                        "memory": psutil.virtual_memory().percent,
                        "disk": psutil.disk_usage('/').percent,
                        "timestamp": str(datetime.now()),
                        "connection_id": id(self)  # Track which connection sent what
                    }
                }
                print(f"📡 Sending metrics: {metrics}")
                await self.send(text_data=json.dumps(metrics))
                await asyncio.sleep(1)  # Wait a second between updates
        except Exception as e:
            print(f"💥 METRICS STREAM FUCKED UP: {str(e)}")

    async def disconnect(self, close_code):
        print(f"💔 Connection {id(self)} fucked off with code: {close_code}")
        pass

    async def receive(self, text_data):
        print(f"GOT SOME FUCKING DATA: {text_data}")
        try:
            await self.send(text_data=json.dumps({
                "type": "metrics_update",
                "data": "Your metrics here, you magnificent bastard"
            }))
        except Exception as e:
            print(f"SHIT BROKE: {str(e)}")