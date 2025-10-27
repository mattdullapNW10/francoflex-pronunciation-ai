import os
import time

import numpy as np
import sounddevice as sd
import soundfile as sf


def record_user_audio(
    output_dir: str = "audio_file",
    file_prefix: str = "user_input",
    duration_seconds: float = 5.0,
    sample_rate: int = 16000,
    channels: int = 1,
) -> str:
    """Record audio from the default microphone and save it as a WAV file.

    Returns the saved file path.
    """
    os.makedirs(output_dir, exist_ok=True)

    input("Press Enter to start recording...")
    print(f"Recording for {duration_seconds} seconds...")

    num_frames = int(duration_seconds * sample_rate)
    recording = sd.rec(num_frames, samplerate=sample_rate, channels=channels, dtype="float32")
    sd.wait()

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{file_prefix}_{timestamp}.wav"
    save_path = os.path.join(output_dir, filename)

    sf.write(save_path, recording, sample_rate)
    print(f"Saved: {save_path}")
    return save_path


if __name__ == "__main__":
    try:
        user_input = input("Enter recording duration in seconds (default 5): ").strip()
        duration = float(user_input) if user_input else 5.0
    except Exception:
        duration = 5.0

    record_user_audio(duration_seconds=duration)


