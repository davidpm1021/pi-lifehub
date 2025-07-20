"""Voice recognition service with error handling"""
import logging
import threading
import queue
import time
from typing import Optional, Callable
from contextlib import contextmanager

from .config import (
    WAKE_WORD, SAMPLE_RATE, CHUNK_SIZE, TIMEOUT_SECONDS,
    MAX_RETRIES, MIC_DEVICE_INDEX, VOICE_COMMANDS, ERROR_MESSAGES
)
from .models import VoiceCommand, VoiceResponse, MicrophoneStatus

logger = logging.getLogger("pi_life_hub.voice")

class VoiceService:
    """Voice recognition service with production error handling"""
    
    def __init__(self):
        self.pyaudio = None
        self.recognizer = None
        self.microphone = None
        self.is_listening = False
        self.command_queue = queue.Queue()
        self.listener_thread = None
        self._initialize_audio()
    
    def _initialize_audio(self):
        """Initialize audio components with error handling"""
        try:
            import pyaudio
            import speech_recognition as sr
            
            self.pyaudio = pyaudio.PyAudio()
            self.recognizer = sr.Recognizer()
            
            # Configure recognizer
            self.recognizer.energy_threshold = 2000
            self.recognizer.dynamic_energy_threshold = True
            
            # Find and configure microphone
            mic_index = self._find_usb_microphone()
            if mic_index is not None:
                self.microphone = sr.Microphone(
                    device_index=mic_index,
                    sample_rate=SAMPLE_RATE,
                    chunk_size=CHUNK_SIZE
                )
                logger.info(f"Initialized microphone at index {mic_index}")
            else:
                logger.warning("No USB microphone found, voice commands disabled")
                
        except ImportError as e:
            logger.error(f"Audio dependencies not installed: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize audio: {e}")
    
    def _find_usb_microphone(self) -> Optional[int]:
        """Find USB microphone device index"""
        if MIC_DEVICE_INDEX is not None:
            return MIC_DEVICE_INDEX
            
        if not self.pyaudio:
            return None
            
        try:
            for i in range(self.pyaudio.get_device_count()):
                info = self.pyaudio.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0 and 'usb' in info['name'].lower():
                    logger.info(f"Found USB microphone: {info['name']} at index {i}")
                    return i
        except Exception as e:
            logger.error(f"Error searching for microphone: {e}")
        
        return None
    
    def get_microphone_status(self) -> MicrophoneStatus:
        """Get current microphone status"""
        if not self.pyaudio:
            return MicrophoneStatus(
                connected=False,
                sample_rate=SAMPLE_RATE,
                error="Audio system not initialized"
            )
        
        mic_index = self._find_usb_microphone()
        if mic_index is None:
            return MicrophoneStatus(
                connected=False,
                sample_rate=SAMPLE_RATE,
                error=ERROR_MESSAGES["no_mic"]
            )
        
        try:
            info = self.pyaudio.get_device_info_by_index(mic_index)
            return MicrophoneStatus(
                connected=True,
                device_name=info['name'],
                device_index=mic_index,
                sample_rate=SAMPLE_RATE
            )
        except Exception as e:
            return MicrophoneStatus(
                connected=False,
                sample_rate=SAMPLE_RATE,
                error=str(e)
            )
    
    @contextmanager
    def _audio_context(self):
        """Context manager for audio operations"""
        if not self.microphone or not self.recognizer:
            yield None
            return
            
        try:
            with self.microphone as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                yield source
        except Exception as e:
            logger.error(f"Audio context error: {e}")
            yield None
    
    def listen_for_command(self) -> VoiceResponse:
        """Listen for a single voice command"""
        if not self.microphone or not self.recognizer:
            return VoiceResponse(
                success=False,
                message=ERROR_MESSAGES["no_mic"]
            )
        
        retry_count = 0
        while retry_count < MAX_RETRIES:
            try:
                with self._audio_context() as source:
                    if not source:
                        return VoiceResponse(
                            success=False,
                            message=ERROR_MESSAGES["service_error"]
                        )
                    
                    logger.info("Listening for command...")
                    audio = self.recognizer.listen(
                        source,
                        timeout=TIMEOUT_SECONDS,
                        phrase_time_limit=5
                    )
                    
                    # Try to recognize speech
                    try:
                        text = self.recognizer.recognize_google(audio).lower()
                        logger.info(f"Recognized: {text}")
                        
                        # Check for wake word
                        if WAKE_WORD in text:
                            # Extract command after wake word
                            command_text = text.split(WAKE_WORD, 1)[1].strip()
                            return self._process_command(command_text)
                        else:
                            # Process direct command without wake word
                            return self._process_command(text)
                            
                    except Exception as e:
                        logger.warning(f"Recognition failed: {e}")
                        retry_count += 1
                        
            except Exception as e:
                logger.error(f"Listen error: {e}")
                retry_count += 1
                time.sleep(0.5)
        
        return VoiceResponse(
            success=False,
            message=ERROR_MESSAGES["timeout"]
        )
    
    def _process_command(self, text: str) -> VoiceResponse:
        """Process recognized text into command"""
        if not text:
            return VoiceResponse(
                success=False,
                message=ERROR_MESSAGES["unknown"]
            )
        
        # Find matching command
        for phrase, action in VOICE_COMMANDS.items():
            if phrase in text:
                return VoiceResponse(
                    success=True,
                    command=text,
                    action=action,
                    message=f"Executing: {action}"
                )
        
        return VoiceResponse(
            success=False,
            command=text,
            message=ERROR_MESSAGES["unknown"]
        )
    
    def start_continuous_listening(self, callback: Callable[[VoiceResponse], None]):
        """Start continuous listening in background thread"""
        if self.is_listening:
            logger.warning("Already listening")
            return
        
        self.is_listening = True
        self.listener_thread = threading.Thread(
            target=self._continuous_listen_worker,
            args=(callback,),
            daemon=True
        )
        self.listener_thread.start()
        logger.info("Started continuous listening")
    
    def _continuous_listen_worker(self, callback: Callable[[VoiceResponse], None]):
        """Worker thread for continuous listening"""
        while self.is_listening:
            try:
                response = self.listen_for_command()
                if response.success:
                    callback(response)
                time.sleep(0.1)  # Small delay between listens
            except Exception as e:
                logger.error(f"Continuous listen error: {e}")
                time.sleep(1)  # Longer delay on error
    
    def stop_listening(self):
        """Stop continuous listening"""
        self.is_listening = False
        if self.listener_thread:
            self.listener_thread.join(timeout=2)
        logger.info("Stopped listening")
    
    def cleanup(self):
        """Clean up audio resources"""
        self.stop_listening()
        if self.pyaudio:
            try:
                self.pyaudio.terminate()
            except Exception as e:
                logger.error(f"Cleanup error: {e}")

# Global service instance
voice_service = VoiceService()