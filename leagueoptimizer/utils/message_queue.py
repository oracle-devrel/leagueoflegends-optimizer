"""
Message queue abstraction layer for the League Optimizer.

This module provides a unified interface for message queue operations
with improved error handling and retry mechanisms.
"""
import json
import time
from typing import Any, Callable, Dict, Optional, Union

import pika
from pika.exceptions import AMQPConnectionError, ChannelClosedByBroker, StreamLostError

from leagueoptimizer.config.settings import CONFIG
from leagueoptimizer.utils.logging import app_logger as logger


class MessageQueueError(Exception):
    """Base exception for message queue errors."""
    pass


class MessageQueue:
    """Message queue implementation with RabbitMQ."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5672,
        username: str = "guest",
        password: str = "guest",
        queue_name: str = "default",
        heartbeat: int = 600,
        blocked_connection_timeout: int = 300,
        max_retries: int = 3,
        retry_delay: int = 5,
    ):
        """
        Initialize the message queue.
        
        Args:
            host: The RabbitMQ host
            port: The RabbitMQ port
            username: The RabbitMQ username
            password: The RabbitMQ password
            queue_name: The name of the queue
            heartbeat: The heartbeat interval in seconds
            blocked_connection_timeout: The blocked connection timeout in seconds
            max_retries: The maximum number of connection retries
            retry_delay: The delay between retries in seconds
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.queue_name = queue_name
        self.heartbeat = heartbeat
        self.blocked_connection_timeout = blocked_connection_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self.connection = None
        self.channel = None
        self.connected = False
    
    def connect(self) -> None:
        """
        Establish a connection to the message queue.
        
        Raises:
            MessageQueueError: If the connection fails after max_retries
        """
        retries = 0
        while retries < self.max_retries:
            try:
                credentials = pika.PlainCredentials(self.username, self.password)
                connection_params = pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    credentials=credentials,
                    heartbeat=self.heartbeat,
                    blocked_connection_timeout=self.blocked_connection_timeout,
                )
                
                self.connection = pika.BlockingConnection(connection_params)
                self.channel = self.connection.channel()
                
                # Declare the queue
                self.channel.queue_declare(queue=self.queue_name, durable=True)
                
                # Declare the dead letter queue
                self.channel.queue_declare(
                    queue=f"{self.queue_name}_dead_letter", durable=True
                )
                
                self.connected = True
                logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
                return
            
            except (AMQPConnectionError, StreamLostError) as e:
                retries += 1
                logger.warning(
                    f"Failed to connect to RabbitMQ (attempt {retries}/{self.max_retries}): {e}"
                )
                if retries < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Failed to connect to RabbitMQ after {self.max_retries} attempts")
                    raise MessageQueueError(f"Failed to connect to RabbitMQ: {e}")
    
    def disconnect(self) -> None:
        """Close the message queue connection."""
        if self.connection and self.connection.is_open:
            self.connection.close()
            self.connected = False
            logger.info("Disconnected from RabbitMQ")
    
    def publish(self, message: Union[str, Dict[str, Any]], retry: bool = True) -> None:
        """
        Publish a message to the queue.
        
        Args:
            message: The message to publish (string or dictionary)
            retry: Whether to retry on failure
            
        Raises:
            MessageQueueError: If the message cannot be published
        """
        if not self.connected:
            self.connect()
        
        # Convert dictionary to JSON string if necessary
        if isinstance(message, dict):
            message = json.dumps(message)
        
        try:
            self.channel.basic_publish(
                exchange="",
                routing_key=self.queue_name,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ),
            )
            logger.debug(f"Published message to queue {self.queue_name}")
        
        except (StreamLostError, ChannelClosedByBroker) as e:
            logger.warning(f"Connection lost while publishing message: {e}")
            if retry:
                logger.info("Reconnecting and retrying...")
                self.connect()
                self.publish(message, retry=False)
            else:
                logger.error("Failed to publish message after reconnect")
                raise MessageQueueError(f"Failed to publish message: {e}")
    
    def consume(self, callback: Callable[[str], None], auto_ack: bool = True) -> None:
        """
        Consume messages from the queue.
        
        Args:
            callback: The callback function to process messages
            auto_ack: Whether to automatically acknowledge messages
            
        Raises:
            MessageQueueError: If consumption fails
        """
        if not self.connected:
            self.connect()
        
        def wrapped_callback(ch, method, properties, body):
            """Wrap the callback to handle errors."""
            try:
                message = body.decode("utf-8")
                logger.debug(f"Received message from queue {self.queue_name}")
                callback(message)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                if not auto_ack:
                    # Reject the message and send to dead letter queue
                    ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
                    logger.warning(f"Message rejected and sent to dead letter queue")
                    
                    # Publish to dead letter queue
                    try:
                        self.channel.basic_publish(
                            exchange="",
                            routing_key=f"{self.queue_name}_dead_letter",
                            body=body,
                        )
                    except Exception as e:
                        logger.error(f"Failed to publish to dead letter queue: {e}")
        
        try:
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=wrapped_callback,
                auto_ack=auto_ack,
            )
            
            logger.info(f"Started consuming from queue {self.queue_name}")
            self.channel.start_consuming()
        
        except (StreamLostError, ChannelClosedByBroker) as e:
            logger.warning(f"Connection lost while consuming: {e}")
            self.connect()
            self.consume(callback, auto_ack)
        
        except KeyboardInterrupt:
            logger.info("Stopping consumer due to keyboard interrupt")
            self.channel.stop_consuming()
            self.disconnect()
        
        except Exception as e:
            logger.error(f"Error consuming from queue: {e}")
            raise MessageQueueError(f"Failed to consume from queue: {e}")


def get_message_queue(queue_name: Optional[str] = None) -> MessageQueue:
    """
    Get a message queue instance based on configuration.
    
    Args:
        queue_name: The name of the queue (defaults to config value)
        
    Returns:
        A message queue instance
    """
    mq_config = CONFIG["message_queue"]
    
    if queue_name is None:
        queue_name = mq_config["queue_name"]
    
    return MessageQueue(
        host=mq_config["host"],
        port=mq_config["port"],
        username=mq_config["username"],
        password=mq_config["password"],
        queue_name=queue_name,
        heartbeat=mq_config["heartbeat"],
        blocked_connection_timeout=mq_config["blocked_connection_timeout"],
    ) 