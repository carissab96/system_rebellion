# core/test_consumer.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging

logger = logging.getLogger(__name__)

class TestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info("=== TEST WEBSOCKET CONNECTION ATTEMPT DETECTED ===")
        logger.info(f"🔍 Test Connection ID: {id(self)}")
        logger.info(f"🔍 Test Connection Path: {self.scope['path']}")
        
        try:
            await self.accept()
            logger.info("✅ TEST CONNECTION SUCCESSFULLY ACCEPTED!")
            await self.send(text_data=json.dumps({
                "type": "test_message",
                "data": "Test websocket connection successful!"
            }))
        except Exception as e:
            logger.error(f"❌ TEST CONNECTION ACCEPTANCE FAILED: {str(e)}")
            logger.exception("Detailed traceback:")
            
    async def disconnect(self, close_code):
        logger.info(f"💔 Test Connection {id(self)} closed with code: {close_code}")
        
    async def receive(self, text_data):
        logger.info(f"📨 Test message received: {text_data}")
        try:
            await self.send(text_data=json.dumps({
                "type": "test_response",
                "data": f"Echo: {text_data}"
            }))
        except Exception as e:
            logger.error(f"❌ Error sending test response: {str(e)}")
