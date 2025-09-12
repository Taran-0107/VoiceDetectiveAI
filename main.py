import os
import whisper
import imageio_ffmpeg as ffmpeg

# Point Whisper to bundled ffmpeg
os.environ["PATH"] = os.path.dirname(ffmpeg.get_ffmpeg_exe()) + os.pathsep + os.environ["PATH"]

# Load model
model = whisper.load_model("base")

filename= "voices/sample/buried_confession.mp3"
# Transcribe
result = model.transcribe(filename)  # works with mp3, wav, m4a, etc.
print("📝 Transcription:", result["text"])

