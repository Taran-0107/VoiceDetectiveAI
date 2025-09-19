import os
import subprocess
import whisper
import imageio_ffmpeg as ffmpeg
import numpy as np
import json
import glob
from datetime import datetime
from voice_analyzer import VoiceAnalyzer
from collections import defaultdict

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

def get_audio_files(directory):
    """Get all audio files from the specified directory"""
    audio_extensions = ['*.mp3', '*.wav', '*.m4a', '*.flac', '*.aac', '*.ogg']
    audio_files = []
    
    for extension in audio_extensions:
        files = glob.glob(os.path.join(directory, extension))
        audio_files.extend(files)
    
    return sorted(audio_files)

def process_multiple_audio_files(audio_directory, json_output_file="final_analysis.json", transcript_output_file="transcripts.txt"):
    """
    Process audio files, creating a file-wise transcript file and a subject-based JSON analysis file.
    """
    
    all_files = get_audio_files(audio_directory)
    
    if not all_files:
        print(f"❌ No audio files found in directory: {audio_directory}")
        return None, None
    
    print(f"🎵 Found {len(all_files)} audio file(s) to process.")

    final_analyses_list = []
    analyzer = VoiceAnalyzer()
    
    ## MODIFICATION START: The logic is now split into two parts. ##
    # Part 1: Transcribe each file and write to the transcript file.
    #         Also, collect transcriptions by subject in memory.
    
    subject_transcriptions = defaultdict(str)
    grouped_files_for_metadata = defaultdict(list) # To get year for shadow_id later

    try:
        with open(transcript_output_file, 'w', encoding='utf-8') as transcript_f:
            print(f"\n🎤 Transcribing files and generating {transcript_output_file}...")
            
            for i, audio_file in enumerate(all_files, 1):
                filename = os.path.basename(audio_file)
                subject_name = filename.split('_')[0]
                
                print(f"   ({i}/{len(all_files)}) Transcribing {filename}...")
                text = transcribe_audio(audio_file, model_size="base").strip()
                
                # Write to transcript file in the new format
                transcript_f.write(f"{filename}\n")
                transcript_f.write(f"{text}\n\n")
                
                # Store text in memory for the consolidated analysis
                subject_transcriptions[subject_name] += text + " "
                grouped_files_for_metadata[subject_name].append(audio_file)

        print(f"✅ Transcripts saved successfully to {transcript_output_file}")

        # Part 2: Analyze the combined transcriptions for each subject.
        print(f"\n🔍 Analyzing combined transcriptions for each subject...")
        successful_analyses_for_summary = []

        for subject_name, combined_text in subject_transcriptions.items():
            print(f"   -> Analyzing subject: {subject_name}")
            
            # Generate shadow_id using the first file found for that subject
            year = os.path.basename(grouped_files_for_metadata[subject_name][0]).split('_')[1]
            shadow_id = f"{subject_name}_{year}"

            analysis = analyzer.analyze_transcription(
                transcription_text=combined_text.strip(),
                shadow_id=shadow_id
            )
            
            if analysis:
                final_analyses_list.append(analysis)
                successful_analyses_for_summary.append(analysis)
            else:
                print(f"   ❌ Failed to analyze {subject_name}")
        
        # Save the final JSON file
        with open(json_output_file, 'w', encoding='utf-8') as f:
            json.dump(final_analyses_list, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Final analysis JSON saved to: {json_output_file}")
        
        return final_analyses_list, successful_analyses_for_summary

    except Exception as e:
        print(f"❌ A critical error occurred: {e}")
        return None, None
    ## MODIFICATION END ##


def generate_consolidated_insights(analyses):
    """Generate consolidated insights from multiple analyses FOR CONSOLE DISPLAY ONLY."""
    # This function's logic remains the same.
    insights = {
        "detected_patterns": [],
        "common_deception_indicators": [],
        "skill_level_distribution": {},
        "programming_languages_mentioned": [],
        "leadership_claims_summary": {},
        "overall_credibility_assessment": ""
    }
    
    # ... (rest of the function is unchanged) ...
    from collections import Counter
    skill_levels = [a.get("revealed_truth", {}).get("skill_mastery", "unknown") for a in analyses]
    deception_patterns = [p.get("lie_type") for a in analyses for p in a.get("deception_patterns", []) if p.get("lie_type")]
    
    if skill_levels:
        insights["skill_level_distribution"] = dict(Counter(skill_levels))
    if deception_patterns:
        deception_counter = Counter(deception_patterns)
        insights["common_deception_indicators"] = [{"pattern": p, "frequency": c} for p, c in deception_counter.most_common(5)]
    
    total_analyses = len(analyses)
    deception_rate = len(deception_patterns) / total_analyses if total_analyses > 0 else 0
    
    if deception_rate > 0.7: credibility = "Low"
    elif deception_rate > 0.4: credibility = "Medium"
    elif deception_rate > 0.1: credibility = "Good"
    else: credibility = "High"
    insights["overall_credibility_assessment"] = f"{credibility} (Deception indicator rate: {deception_rate:.1%})"
    
    return insights


if __name__ == "__main__":
    audio_directory = "voices/audio"
    
    if not os.path.exists(audio_directory):
        os.makedirs(audio_directory, exist_ok=True)
        print(f"❌ Directory not found, created at: {audio_directory}")
        print("Please add audio files to this directory and run again.")
    else:
        print(f"🎯 Processing all audio files from: {audio_directory}")
        
        final_json, summary_data = process_multiple_audio_files(
            audio_directory=audio_directory,
            json_output_file="final_analysis.json",
            transcript_output_file="transcripts.txt"
        )
        
        if final_json:
            print(f"\n{'='*60}")
            print("🎉 PROCESSING COMPLETE 🎉")
            print(f"📄 Final JSON analysis saved to: final_analysis.json")
            print(f"📝 Transcripts saved to: transcripts.txt")
            
            # Display console summary
            insights = generate_consolidated_insights(summary_data)
            print(f"\n📊 CONSOLE SUMMARY")
            print(f"{'-'*20}")
            print(f"   Subjects Analyzed: {len(summary_data)}")
            print(f"   Overall Credibility: {insights.get('overall_credibility_assessment', 'N/A')}")
            print(f"   Top Deception Pattern: {insights['common_deception_indicators'][0]['pattern'] if insights['common_deception_indicators'] else 'N/A'}")
            print(f"{'='*60}")
        else:
            print(f"\n❌ Failed to complete the analysis.")