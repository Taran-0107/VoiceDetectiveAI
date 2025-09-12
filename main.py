import os
import subprocess
import whisper
import imageio_ffmpeg as ffmpeg
import numpy as np

# Get the bundled ffmpeg binary path
ffmpeg_bin = ffmpeg.get_ffmpeg_exe()

# Monkey-patch Whisper's audio loader to use imageio-ffmpeg binary
import whisper.audio as wa
def load_audio_with_imageio(path: str):
    cmd = [
        ffmpeg_bin, "-nostdin", "-threads", "0",
        "-i", path,
        "-f", "s16le",
        "-ac", "1",
        "-ar", str(wa.SAMPLE_RATE),
        "-"
    ]
    out = subprocess.run(cmd, capture_output=True, check=True).stdout
    return wa.np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0

wa.load_audio = load_audio_with_imageio  # override default

def transcribe_audio(filename, model_size="base"):
    model = whisper.load_model(model_size)
    result = model.transcribe(filename)
    return result["text"]

if __name__ == "__main__":
    filename = "voices/sample/drifted_anecdote.mp3"

    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
    else:
        text = transcribe_audio(filename, model_size="base")
        print("\n📝 Transcription:")
        print(text)


