"""
Redis Service
Handles state management and caching for the Assistive AI Platform
"""

import time
import json
import logging
from typing import Optional, Any, Dict, List
import redis
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RedisService:
    """Service for Redis-based state management and caching"""

    def __init__(self, host: str = 'localhost', port: int = 6379,
                 db: int = 0, password: Optional[str] = None,
                 default_ttl: int = 300):
        """
        Initialize the Redis service

        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            password: Redis password (if required)
            default_ttl: Default time-to-live for cached items in seconds
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.default_ttl = default_ttl
        self.client = None
        self.is_connected = False

        # Key prefixes for different types of data
        self.KEY_PREFIX_FRAME_HASH = "frame_hash:"
        self.KEY_PREFIX_INFERENCE_RESULT = "inference:"
        self.KEY_PREFIX_OCR_RESULT = "ocr:"
        self.KEY_PREFIX_VLM_RESULT = "vlm:"
        self.KEY_PREFIX_SESSION_STATE = "session:"

        # Connect to Redis
        self._connect()

    def _connect(self):
        """Establish connection to Redis server"""
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True,  # Automatically decode responses to strings
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )

            # Test connection
            self.client.ping()
            self.is_connected = True
            logger.info(f"Connected to Redis at {self.host}:{self.port}")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.is_connected = False
            self.client = None

    def _get_key(self, prefix: str, identifier: str) -> str:
        """Generate a full key with prefix"""
        return f"{prefix}{identifier}"

    def set_frame_hash(self, frame_hash: str, ttl: Optional[int] = None) -> bool:
        """
        Store a frame hash to prevent duplicate processing

        Args:
            frame_hash: Hash of the frame
            ttl: Time-to-live in seconds (uses default if None)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            return False

        try:
            key = self._get_key(self.KEY_PREFIX_FRAME_HASH, frame_hash)
            ttl = ttl or self.default_ttl
            result = self.client.setex(key, ttl, "1")
            return bool(result)
        except Exception as e:
            logger.error(f"Error setting frame hash: {e}")
            return False

    def get_frame_hash(self, frame_hash: str) -> bool:
        """
        Check if a frame hash exists (indicating recent processing)

        Args:
            frame_hash: Hash of the frame to check

        Returns:
            True if frame was recently processed, False otherwise
        """
        if not self.is_connected:
            return False

        try:
            key = self._get_key(self.KEY_PREFIX_FRAME_HASH, frame_hash)
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking frame hash: {e}")
            return False

    def set_inference_result(self, frame_hash: str, result: Dict[str, Any],
                           ttl: Optional[int] = None) -> bool:
        """
        Store inference (object detection) result for a frame

        Args:
            frame_hash: Hash of the frame
            result: Inference result dictionary
            ttl: Time-to-live in seconds (uses default if None)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            return False

        try:
            key = self._get_key(self.KEY_PREFIX_INFERENCE_RESULT, frame_hash)
            ttl = ttl or self.default_ttl
            value = json.dumps(result)
            result = self.client.setex(key, ttl, value)
            return bool(result)
        except Exception as e:
            logger.error(f"Error setting inference result: {e}")
            return False

    def get_inference_result(self, frame_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get inference result for a frame hash

        Args:
            frame_hash: Hash of the frame

        Returns:
            Inference result dictionary or None if not found/expired
        """
        if not self.is_connected:
            return None

        try:
            key = self._get_key(self.KEY_PREFIX_INFERENCE_RESULT, frame_hash)
            value = self.client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            logger.error(f"Error getting inference result: {e}")
            return None

    def set_ocr_result(self, frame_hash: str, result: Dict[str, Any],
                      ttl: Optional[int] = None) -> bool:
        """
        Store OCR result for a frame

        Args:
            frame_hash: Hash of the frame
            result: OCR result dictionary
            ttl: Time-to-live in seconds (uses default if None)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            return False

        try:
            key = self._get_key(self.KEY_PREFIX_OCR_RESULT, frame_hash)
            ttl = ttl or self.default_ttl
            value = json.dumps(result)
            result = self.client.setex(key, ttl, value)
            return bool(result)
        except Exception as e:
            logger.error(f"Error setting OCR result: {e}")
            return False

    def get_ocr_result(self, frame_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get OCR result for a frame hash

        Args:
            frame_hash: Hash of the frame

        Returns:
            OCR result dictionary or None if not found/expired
        """
        if not self.is_connected:
            return None

        try:
            key = self._get_key(self.KEY_PREFIX_OCR_RESULT, frame_hash)
            value = self.client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            logger.error(f"Error getting OCR result: {e}")
            return None

    def set_vlm_result(self, frame_hash: str, result: Dict[str, Any],
                      ttl: Optional[int] = None) -> bool:
        """
        Store VLM (Vision-Language Model) result for a frame

        Args:
            frame_hash: Hash of the frame
            result: VLM result dictionary
            ttl: Time-to-live in seconds (uses default if None)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            return False

        try:
            key = self._get_key(self.KEY_PREFIX_VLM_RESULT, frame_hash)
            ttl = ttl or self.default_ttl
            value = json.dumps(result)
            result = self.client.setex(key, ttl, value)
            return bool(result)
        except Exception as e:
            logger.error(f"Error setting VLM result: {e}")
            return False

    def get_vlm_result(self, frame_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get VLM result for a frame hash

        Args:
            frame_hash: Hash of the frame

        Returns:
            VLM result dictionary or None if not found/expired
        """
        if not self.is_connected:
            return None

        try:
            key = self._get_key(self.KEY_PREFIX_VLM_RESULT, frame_hash)
            value = self.client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            logger.error(f"Error getting VLM result: {e}")
            return None

    def set_session_state(self, session_id: str, state: Dict[str, Any],
                         ttl: Optional[int] = None) -> bool:
        """
        Store session state data

        Args:
            session_id: Unique session identifier
            state: Session state dictionary
            ttl: Time-to-live in seconds (uses default if None)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            return False

        try:
            key = self._get_key(self.KEY_PREFIX_SESSION_STATE, session_id)
            ttl = ttl or self.default_ttl
            value = json.dumps(state)
            result = self.client.setex(key, ttl, value)
            return bool(result)
        except Exception as e:
            logger.error(f"Error setting session state: {e}")
            return False

    def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session state data

        Args:
            session_id: Unique session identifier

        Returns:
            Session state dictionary or None if not found/expired
        """
        if not self.is_connected:
            return None

        try:
            key = self._get_key(self.KEY_PREFIX_SESSION_STATE, session_id)
            value = self.client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            logger.error(f"Error getting session state: {e}")
            return None

    def delete_key(self, key: str) -> bool:
        """
        Delete a key from Redis

        Args:
            key: Key to delete

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            return False

        try:
            result = self.client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting key: {e}")
            return False

    def flush_all(self) -> bool:
        """
        Flush all data from the current database (use with caution)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            return False

        try:
            self.client.flushdb()
            logger.warning("Redis database flushed")
            return True
        except Exception as e:
            logger.error(f"Error flushing Redis database: {e}")
            return False

    def get_info(self) -> Dict[str, Any]:
        """
        Get Redis server information and statistics

        Returns:
            Dictionary with Redis info or empty dict if not connected
        """
        if not self.is_connected:
            return {}

        try:
            info = self.client.info()
            return dict(info)
        except Exception as e:
            logger.error(f"Error getting Redis info: {e}")
            return {}

    def ping(self) -> bool:
        """
        Ping the Redis server to check connection

        Returns:
            True if connected and responsive, False otherwise
        """
        if not self.is_connected:
            return False

        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Error pinging Redis: {e}")
            self.is_connected = False
            return False


# Singleton instance for reuse
_redis_service = None


def get_redis_service(host: str = 'localhost', port: int = 6379,
                     db: int = 0, password: Optional[str] = None,
                     default_ttl: int = 300) -> RedisService:
    """
    Get or create the singleton Redis service instance

    Args:
        host: Redis server host
        port: Redis server port
        db: Redis database number
        password: Redis password (if required)
        default_ttl: Default time-to-live for cached items in seconds

    Returns:
        RedisService instance
    """
    global _redis_service
    if _redis_service is None:
        _redis_service = RedisService(host, port, db, password, default_ttl)
    return _redis_service