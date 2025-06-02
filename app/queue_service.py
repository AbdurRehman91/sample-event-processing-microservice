import os
import boto3
import json
import structlog
from typing import Dict, Any
from datetime import datetime
from botocore.config import Config
from app.config import settings


logger = structlog.get_logger()

class QueueService:
    def __init__(self):
        self.aws_region = settings.aws_region
        self.queue_name = "events-queue"
        self.queue_url = None
        self.queue_obj = None
        boto3_config = Config(
            signature_version='v3',
            connect_timeout=5,
            read_timeout=10,
            retries={'max_attempts': 3},
        )
        self.sqs_resource = boto3.resource(
            'sqs',
            region_name=self.aws_region,
            endpoint_url=settings.elasticmq_endpoint_url,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            use_ssl=False, 
            config=boto3_config

            )
        
    async def initialize_queue_with_client(self):
        """Alternative initialization using SQS client."""
        if self.queue_obj:
            return
            
        sqs_client = self.sqs_resource.meta.client
        
        try:
            # Try to get queue URL
            response = sqs_client.get_queue_url(QueueName=self.queue_name)
            self.queue_url = response['QueueUrl']
            self.queue_obj = self.sqs_resource.Queue(self.queue_url)
            logger.info(f"Found existing queue: {self.queue_url}")
            
        except sqs_client.exceptions.QueueDoesNotExist:
            logger.warning(f"Queue '{self.queue_name}' does not exist, attempting to create...")
            try:
                # Create queue
                response = sqs_client.create_queue(QueueName=self.queue_name)
                self.queue_url = response['QueueUrl']
                self.queue_obj = self.sqs_resource.Queue(self.queue_url)
                logger.info(f"Queue '{self.queue_name}' created with URL: {self.queue_url}")
            except Exception as create_error:
                logger.error(f"Failed to create queue: {create_error}")
                raise
                
        except Exception as e:
            logger.error(f"Failed to initialize queue: {e}")
            raise

    async def initialize_queue(self):
        """Initializes and gets the queue URL for the client."""
        if self.queue_obj:
            return
        try:
            self.queue_obj = self.sqs_resource.get_queue_by_name(QueueName=self.queue_name)
            self.queue_url = self.queue_obj.url
        except self.sqs_resource.meta.client.exceptions.QueueDoesNotExist:    
            logger.warning(f"Queue '{self.queue_name}' does not exist, attempting to create...")
            self.queue_obj = self.sqs_resource.create_queue(QueueName=self.queue_name)
            self.queue_url = self.queue_obj.url
            logger.info(f"Queue '{self.queue_name}' created with URL: {self.queue_url}")
        except Exception as e:
            logger.error(f"Failed to initialize queue: {e}")
            raise

    async def send_event(self, event_data: Dict[str, Any]) -> str:
        """Send event to SQS queue"""
        try:
            await self.initialize_queue_with_client() # Ensure queue URL is set before sending
            message_body = json.dumps({
                **event_data,
                "timestamp": event_data["timestamp"].isoformat() if isinstance(event_data["timestamp"], datetime) else event_data["timestamp"]
            })
            logger.info("message body is :", message_body)
            response = self.queue_obj.send_message(
                MessageBody=message_body,
                QueueUrl=self.queue_obj.url,
                MessageAttributes={
                    'event_type': {
                        'StringValue': event_data['event_type'],
                        'DataType': 'String'
                    },
                    'user_id': {
                        'StringValue': event_data['user_id'],
                        'DataType': 'String'
                    }
                }
            )
            
            logger.info("Event sent to queue", message_id=response['MessageId'])
            return response['MessageId']
            
        except Exception as e:
            logger.error(" exception is :", str(e))
            logger.error("Failed to send event to queue", error=str(e))
            raise
    
    async def receive_events(self, max_messages: int = 10):
        """Receive events from SQS queue"""
        await self.initialize_queue_with_client()
        try:    
            response_messages = self.queue_obj.receive_messages(
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=20,  # Long polling
                MessageAttributeNames=['All']
            )
            logger.info(f"Received {len(response_messages)} messages from queue '{self.queue_name}'")
            received_events = []
            for message in response_messages:
                try:
                    event_data = json.loads(message.body)
                    event_data['MessageAttributes'] = {
                        k: v.get('StringValue') for k, v in message.message_attributes.items()
                    } if message.message_attributes else {}
                    event_data['ReceiptHandle'] = message.receipt_handle
                    received_events.append(event_data)

                except json.JSONDecodeError as jde:
                    logger.error(f"Failed to decode message body as JSON: {message.body}", error=str(jde))
                except KeyError as ke:
                    logger.error(f"Missing expected key in SQS message: {str(ke)}", message=message.body)

            logger.info(f"Received {len(received_events)} events from queue.")
            return received_events
            
        except Exception as e:
            logger.error("Failed to receive events from queue", error=str(e))
            raise
    
    async def delete_message(self, receipt_handle: str):
        """Delete processed message from queue"""
        await self.initialize_queue()
        try:
            self.queue_obj.delete_messages(
                Entries=[
                    {
                        'Id': f"msg-{receipt_handle}", # Unique ID for this specific batch entry
                        'ReceiptHandle': receipt_handle
                    }
                ]
            )
            logger.info("Message deleted from queue")
        except Exception as e:
            logger.error("Failed to delete message from queue", error=str(e))
            raise