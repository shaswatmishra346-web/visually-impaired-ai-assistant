"""
TTS Service
Handles text-to-speech conversion for audio output and feedback
Non-blocking implementation with priority queue and emergency interrupt support
"""

import time
import logging
import threading
import queue
from typing import Optional, Dict, Any
import pyttsx3

logger = logging.getLogger(__name__)


class TTSService:
    """Service for text-to-speech conversion with priority handling and interrupt support"""

    def __init__(self, rate: int = 200, volume: float = 0.9):
        """
        Initialize the TTS service

        Args:
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
        """
        self.rate = rate
        self.volume = volume
        self.engine = None
        self.speech_queue = queue.PriorityQueue()
        self.is_speaking = False
        self.current_utterance = None
        self.speech_thread = None
        self.stop_event = threading.Event()
        self.interrupt_event = threading.Event()

        # Priority levels: lower number = higher priority
        # 0: Emergency alerts (highest priority, can interrupt)
        # 1: Standard scene descriptions
        # 2: System notifications
        self.PRIORITY_EMERGENCY = 0
        self.PRIORITY_STANDARD = 1
        self.PRIORITY_SYSTEM = 2

        # Initialize the TTS engine
        self._initialize_engine()

        # Start the speech processing thread
        self._start_speech_thread()

        logger.info(f"TTSService initialized with rate: {rate} WPM, volume: {volume}")

    def _initialize_engine(self):
        """Initialize the pyttsx3 TTS engine"""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)

            # Set up event callbacks for non-blocking operation
            self.engine.connect('started-utterance', self._on_start)
            self.engine.connect('finished-utterance', self._on_end)
            self.engine.connect('error', self._on_error)

            # Optional: Set voice properties
            voices = self.engine.getProperty('voices')
            if voices:
                # Prefer a female voice if available (often clearer for UI)
                for voice in voices:
                    if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
                else:
                    # Use first available voice
                    self.engine.setProperty('voice', voices[0].id)

            # Start the engine loop (non-blocking)
            self.engine.startLoop(False)

            logger.info("TTS engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            # Create a dummy engine that logs instead of speaking
            self.engine = None

    def _start_speech_thread(self):
        """Start the background thread for processing speech queue"""
        self.stop_event.clear()
        self.interrupt_event.clear()
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()
        logger.info("TTS speech thread started")

    def _on_start(self, name):
        """Callback when utterance starts"""
        self.is_speaking = True
        logger.debug(f"TTS started: {name}")

    def _on_end(self, name, completed):
        """Callback when utterance ends"""
        self.is_speaking = False
        self.current_utterance = None
        logger.debug(f"TTS finished: {name} (completed: {completed})")

    def _on_error(self, name, exception):
        """Callback on TTS error"""
        self.is_speaking = False
        self.current_utterance = None
        logger.error(f"TTS error: {exception}")

    def _speech_worker(self):
        """Background worker that processes the speech queue"""
        while not self.stop_event.is_set():
            try:
                # Process engine events (non-blocking)
                if self.engine:
                    self.engine.iterate()

                # Get item from queue with timeout to allow checking stop_event
                try:
                    priority, timestamp, text, interruptible = self.speech_queue.get(timeout=0.05)
                except queue.Empty:
                    continue

                # Check if we should stop
                if self.stop_event.is_set():
                    break

                # Handle emergency interrupt
                if priority == self.PRIORITY_EMERGENCY and self.is_speaking:
                    # Interrupt current speech
                    logger.info("Emergency interrupt: stopping current speech")
                    self._interrupt_current_speech()

                # Speak the text
                self._speak_text(text, interruptible)

                # Mark task as done
                self.speech_queue.task_done()

            except Exception as e:
                logger.error(f"Error in TTS speech worker: {e}")

    def _interrupt_current_speech(self):
        """Interrupt currently playing speech"""
        if self.engine and self.is_speaking:
            try:
                self.engine.stop()
                self.is_speaking = False
                self.current_utterance = None
            except Exception as e:
                logger.error(f"Error interrupting speech: {e}")

    def _speak_text(self, text: str, interruptible: bool = False):
        """
        Speak the given text using the TTS engine (non-blocking)

        Args:
            text: Text to speak
            interruptible: Whether this utterance can be interrupted by emergency
        """
        if not self.engine:
            logger.info(f"TTS (engine not available): {text}")
            return

        try:
            self.current_utterance = text
            self.is_speaking = True
            logger.debug(f"Speaking: {text[:100]}{'...' if len(text) > 100 else ''}")

            # Queue the utterance (non-blocking)
            self.engine.say(text)

            # Wait for this utterance to complete (with interrupt check)
            self._wait_for_utterance(interruptible)

        except Exception as e:
            logger.error(f"Error during TTS speech: {e}")
            self.is_speaking = False
            self.current_utterance = None

    def _wait_for_utterance(self, interruptible: bool):
        """
        Wait for current utterance to complete, checking for interrupts

        Args:
            interruptible: Whether this utterance can be interrupted
        """
        while self.is_speaking and not self.stop_event.is_set():
            if self.engine:
                self.engine.iterate()

            # Check for emergency interrupt
            if interruptible:
                try:
                    # Peek at queue without removing
                    with self.speech_queue.mutex:
                        if self.speech_queue.queue:
                            next_priority = self.speech_queue.queue[0][0]
                            if next_priority == self.PRIORITY_EMERGENCY:
                                logger.info("Emergency queued, interrupting current speech")
                                self._interrupt_current_speech()
                                break
                except Exception:
                    pass

            time.sleep(0.01)  # Small sleep to prevent busy waiting

    def speak(self, text: str, priority: int = None, block: bool = False, interruptible: bool = True):
        """
        Add text to the speech queue with specified priority

        Args:
            text: Text to speak
            priority: Priority level (lower = higher priority).
                     If None, uses PRIORITY_STANDARD
            block: If True, wait until speech completes before returning
            interruptible: Whether this utterance can be interrupted by emergency
        """
        if not text or not text.strip():
            return

        if priority is None:
            priority = self.PRIORITY_STANDARD

        # Add to queue with timestamp to ensure FIFO for same priority
        timestamp = time.time()
        self.speech_queue.put((priority, timestamp, text, interruptible))

        logger.debug(f"Queued speech (priority={priority}, interruptible={interruptible}): "
                     f"{text[:50]}{'...' if len(text) > 50 else ''}")

        if block:
            # Wait for queue to be empty
            self.speech_queue.join()

    def speak_emergency(self, text: str, block: bool = False):
        """
        Speak emergency text with highest priority (interrupts current speech if needed)

        Args:
            text: Emergency text to speak
            block: If True, wait until speech completes before returning
        """
        logger.warning(f"Emergency TTS: {text}")
        self.speak(text, priority=self.PRIORITY_EMERGENCY, block=block, interruptible=False)

    def speak_standard(self, text: str, block: bool = False):
        """
        Speak standard text with normal priority

        Args:
            text: Standard text to speak
            block: If True, wait until speech completes before returning
        """
        self.speak(text, priority=self.PRIORITY_STANDARD, block=block, interruptible=True)

    def speak_system(self, text: str, block: bool = False):
        """
        Speak system notification text with low priority

        Args:
            text: System text to speak
            block: If True, wait until speech completes before returning
        """
        self.speak(text, priority=self.PRIORITY_SYSTEM, block=block, interruptible=True)

    def stop(self):
        """Stop the TTS service and clean up resources"""
        logger.info("Stopping TTS service")
        self.stop_event.set()

        # Interrupt any current speech
        self._interrupt_current_speech()

        # Clear the queue
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except queue.Empty:
                break

        if self.speech_thread and self.speech_thread.is_alive():
            self.speech_thread.join(timeout=2.0)

        if self.engine:
            try:
                self.engine.endLoop()
                self.engine.stop()
            except Exception as e:
                logger.error(f"Error stopping TTS engine: {e}")
            self.engine = None

    def is_busy(self) -> bool:
        """
        Check if the TTS service is currently speaking or has queued items

        Returns:
            True if currently speaking or queue not empty, False otherwise
        """
        return self.is_speaking or not self.speech_queue.empty()

    def get_queue_size(self) -> int:
        """
        Get the number of items in the speech queue

        Returns:
            Number of queued speech items
        """
        return self.speech_queue.qsize()

    def clear_queue(self):
        """Clear all pending speech from the queue"""
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except queue.Empty:
                break
        logger.info("TTS queue cleared")


# Singleton instance for reuse
_tts_service = None


def get_tts_service(rate: int = 200, volume: float = 0.9) -> TTSService:
    """
    Get or create the singleton TTS service instance

    Args:
        rate: Speech rate (words per minute)
        volume: Volume level (0.0 to 1.0)

    Returns:
        TTSService instance
    """
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService(rate, volume)
    return _tts_service