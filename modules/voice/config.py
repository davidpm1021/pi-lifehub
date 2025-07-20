"""Voice module configuration"""
import os

# Voice recognition settings
WAKE_WORD = os.getenv("LIFEHUB_WAKE_WORD", "hey hub")
SAMPLE_RATE = int(os.getenv("LIFEHUB_VOICE_SAMPLE_RATE", "16000"))
CHUNK_SIZE = int(os.getenv("LIFEHUB_VOICE_CHUNK_SIZE", "1024"))
TIMEOUT_SECONDS = int(os.getenv("LIFEHUB_VOICE_TIMEOUT", "5"))
MAX_RETRIES = int(os.getenv("LIFEHUB_VOICE_RETRIES", "3"))

# Audio device settings
MIC_DEVICE_INDEX = os.getenv("LIFEHUB_MIC_DEVICE_INDEX", None)
if MIC_DEVICE_INDEX:
    MIC_DEVICE_INDEX = int(MIC_DEVICE_INDEX)

# Command mappings
VOICE_COMMANDS = {
    "what time": "time",
    "show weather": "weather",
    "add task": "add_todo",
    "show tasks": "show_todos",
    "start timer": "timer",
    "show photos": "photos",
    "next photo": "next_photo",
    "previous photo": "prev_photo",
    "help": "help"
}

# Error messages
ERROR_MESSAGES = {
    "no_mic": "Microphone not detected. Please check USB connection.",
    "timeout": "No voice command detected. Please try again.",
    "unknown": "Sorry, I didn't understand that command.",
    "service_error": "Voice service temporarily unavailable."
}