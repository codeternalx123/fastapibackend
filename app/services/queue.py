from typing import Dict, Any, Optional, List
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class QueueService:
    """Service for handling distributed message queues"""
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self.consumer = None
        self.running = False
        
    async def start(self) -> None:
        """Start queue service"""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers
            )
            await self.producer.start()
            
            self.consumer = AIOKafkaConsumer(
                settings.KAFKA_TOPIC,
                bootstrap_servers=self.bootstrap_servers,
                group_id=settings.KAFKA_GROUP
            )
            await self.consumer.start()
            
            self.running = True
            logger.info("Queue service started")
            
        except Exception as e:
            logger.error(f"Queue service start error: {str(e)}")
            raise
            
    async def stop(self) -> None:
        """Stop queue service"""
        try:
            if self.producer:
                await self.producer.stop()
            if self.consumer:
                await self.consumer.stop()
                
            self.running = False
            logger.info("Queue service stopped")
            
        except Exception as e:
            logger.error(f"Queue service stop error: {str(e)}")
            raise
            
    async def send_message(
        self,
        topic: str,
        message: Dict[str, Any]
    ) -> bool:
        """Send message to queue"""
        try:
            if not self.running:
                raise RuntimeError("Queue service not running")
                
            # Serialize message
            value = json.dumps(message).encode()
            
            # Send message
            await self.producer.send_and_wait(
                topic,
                value
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Message send error: {str(e)}")
            return False
            
    async def send_batch(
        self,
        topic: str,
        messages: List[Dict[str, Any]]
    ) -> bool:
        """Send batch of messages"""
        try:
            if not self.running:
                raise RuntimeError("Queue service not running")
                
            # Prepare batch
            batch = self.producer.create_batch()
            
            for message in messages:
                value = json.dumps(message).encode()
                batch.append(
                    key=None,
                    value=value,
                    timestamp=None
                )
                
            # Send batch
            await self.producer.send_batch(batch, topic)
            
            return True
            
        except Exception as e:
            logger.error(f"Batch send error: {str(e)}")
            return False
            
    async def receive_messages(
        self,
        timeout_ms: int = 1000
    ) -> List[Dict[str, Any]]:
        """Receive messages from queue"""
        try:
            if not self.running:
                raise RuntimeError("Queue service not running")
                
            messages = []
            
            # Read messages
            async for msg in self.consumer:
                try:
                    value = json.loads(msg.value.decode())
                    messages.append(value)
                except json.JSONDecodeError as e:
                    logger.error(f"Message decode error: {str(e)}")
                    continue
                    
            return messages
            
        except Exception as e:
            logger.error(f"Message receive error: {str(e)}")
            return []
            
    async def process_messages(
        self,
        handler: callable,
        batch_size: Optional[int] = None
    ) -> None:
        """Process messages with handler function"""
        try:
            if not self.running:
                raise RuntimeError("Queue service not running")
                
            batch = []
            
            async for msg in self.consumer:
                try:
                    value = json.loads(msg.value.decode())
                    
                    if batch_size:
                        batch.append(value)
                        if len(batch) >= batch_size:
                            await handler(batch)
                            batch = []
                    else:
                        await handler([value])
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Message decode error: {str(e)}")
                    continue
                except Exception as e:
                    logger.error(
                        f"Message processing error: {str(e)}"
                    )
                    continue
                    
            # Process remaining batch
            if batch:
                await handler(batch)
                
        except Exception as e:
            logger.error(f"Message processing error: {str(e)}")
            raise
            
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        try:
            if not self.running:
                raise RuntimeError("Queue service not running")
                
            # Get metrics from consumer
            metrics = self.consumer.metrics()
            
            return {
                'messages_consumed': metrics.get(
                    'consumer-fetch-manager-metrics',
                    {}
                ).get('records-consumed-total', 0),
                'bytes_consumed': metrics.get(
                    'consumer-fetch-manager-metrics',
                    {}
                ).get('bytes-consumed-total', 0),
                'lag': metrics.get(
                    'consumer-fetch-manager-metrics',
                    {}
                ).get('records-lag-max', 0)
            }
            
        except Exception as e:
            logger.error(f"Queue stats error: {str(e)}")
            return {
                'messages_consumed': 0,
                'bytes_consumed': 0,
                'lag': 0
            }