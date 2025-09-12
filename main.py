import whisper

def transcribe_audio(audio_path):
    # Load Whisper model (use "tiny", "base", "small", "medium", "large")
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]


filename= "voices/sample/buried_confession.mp3"
if __name__ == "__main__":
    audio_file = filename  # replace with your audio file
    text = transcribe_audio(audio_file)
    print("📝 Transcription:", text)
