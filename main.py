import os
import subprocess
import whisper
import imageio_ffmpeg as ffmpeg
import numpy as np
import json
import glob
from datetime import datetime
from voice_analyzer import VoiceAnalyzer
from collections import defaultdict # Import defaultdict for easier grouping

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

def process_multiple_audio_files(audio_directory, output_file="comprehensive_truth_weaver_analysis.json"):
    """
    Process all audio files in the directory, grouping them by subject,
    and create a comprehensive analysis.
    """
    
    # Get all audio files
    all_files = get_audio_files(audio_directory)
    
    if not all_files:
        print(f"❌ No audio files found in directory: {audio_directory}")
        return None

    ## MODIFICATION START: Group files by subject name (e.g., 'atlas', 'eos') ##
    
    # Group files using the prefix of the filename (e.g., "atlas_2025_1.mp3" -> "atlas")
    grouped_files = defaultdict(list)
    for f in all_files:
        subject_name = os.path.basename(f).split('_')[0]
        grouped_files[subject_name].append(f)
        
    total_subjects = len(grouped_files)
    print(f"🎵 Found {len(all_files)} audio files for {total_subjects} unique subject(s).")
    for subject, files in grouped_files.items():
        print(f"  - Subject '{subject}': {len(files)} file(s)")

    ## MODIFICATION END ##
    
    # Initialize the comprehensive analysis structure
    comprehensive_analysis = {
        "metadata": {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_files_processed": len(all_files),
            "total_subjects_analyzed": total_subjects,
            "audio_directory": audio_directory,
            "version": "1.0"
        },
        "individual_analyses": [],
        "consolidated_insights": {
            "detected_patterns": [],
            "common_deception_indicators": [],
            "skill_level_distribution": {},
            "programming_languages_mentioned": [],
            "leadership_claims_summary": {},
            "overall_credibility_assessment": ""
        }
    }
    
    # Initialize analyzer
    analyzer = VoiceAnalyzer()
    successful_analyses = []
    
    ## MODIFICATION START: Loop through subjects instead of individual files ##
    
    # Process each subject group
    for i, (subject_name, subject_files) in enumerate(grouped_files.items(), 1):
        print(f"\n{'='*60}")
        print(f"👤 Processing Subject {i}/{total_subjects}: {subject_name}")
        print(f"{'='*60}")
        
        combined_text = ""
        individual_file_metadata = []
        
        try:
            # Transcribe and concatenate all files for the current subject
            print(f"🎤 Transcribing {len(subject_files)} audio file(s) for {subject_name}...")
            for audio_file in subject_files:
                filename = os.path.basename(audio_file)
                print(f"   -> Transcribing {filename}...")
                text = transcribe_audio(audio_file, model_size="base")
                combined_text += text + " "  # Add space between transcriptions
                individual_file_metadata.append({
                    "filename": filename,
                    "filepath": audio_file,
                    "transcription_length": len(text)
                })

            combined_text = combined_text.strip()
            print(f"📝 Total transcription length for {subject_name}: {len(combined_text)} characters")
            
            # Generate a single shadow_id for the subject
            # e.g., "atlas_2025" from "atlas_2025_1.mp3"
            year = os.path.basename(subject_files[0]).split('_')[1]
            shadow_id = f"{subject_name}_{year}"
            
            print(f"🔍 Analyzing combined transcription with Truth Weaver (ID: {shadow_id})...")
            
            # Analyze the combined text with Truth Weaver
            analysis = analyzer.analyze_transcription(
                transcription_text=combined_text,
                shadow_id=shadow_id
            )
            
            if analysis:
                # Add subject metadata to the analysis
                subject_analysis = {
                    "subject_metadata": {
                        "subject_name": subject_name,
                        "shadow_id": shadow_id,
                        "processed_files": [meta['filename'] for meta in individual_file_metadata],
                        "full_transcription_text": combined_text,
                        "total_transcription_length": len(combined_text)
                    },
                    "truth_weaver_analysis": analysis
                }
                
                comprehensive_analysis["individual_analyses"].append(subject_analysis)
                successful_analyses.append(analysis)
                
                print(f"✅ Analysis completed for {subject_name}")
                
                # Show brief summary
                revealed_truth = analysis.get("revealed_truth", {})
                print(f"📊 Quick Summary for {subject_name}:")
                print(f"   Experience: {revealed_truth.get('programming_experience', 'N/A')}")
                print(f"   Skill Level: {revealed_truth.get('skill_mastery', 'N/A')}")
                
            else:
                print(f"❌ Failed to analyze {subject_name}")
                
        except Exception as e:
            print(f"❌ Error processing {subject_name}: {e}")
            continue

    ## MODIFICATION END ##
    
    # Generate consolidated insights from the per-subject analyses
    if successful_analyses:
        print(f"\n{'='*60}")
        print("🧠 Generating Consolidated Insights...")
        print(f"{'='*60}")
        
        comprehensive_analysis["consolidated_insights"] = generate_consolidated_insights(successful_analyses)
        
        # Save comprehensive analysis
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(comprehensive_analysis, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Comprehensive Truth Weaver's Analysis saved to: {output_file}")
            print(f"📊 Successfully processed {len(successful_analyses)}/{total_subjects} subjects")
            
            # Display summary
            print(f"\n📈 Analysis Summary:")
            print(f"   Total Files: {comprehensive_analysis['metadata']['total_files_processed']}")
            print(f"   Successful Subjects: {len(successful_analyses)}")
            
            return comprehensive_analysis, output_file
            
        except Exception as e:
            print(f"❌ Error saving comprehensive analysis: {e}")
            return None, None
    else:
        print("❌ No successful analyses to consolidate")
        return None, None

def generate_consolidated_insights(analyses):
    """Generate consolidated insights from multiple analyses"""
    
    insights = {
        "detected_patterns": [],
        "common_deception_indicators": [],
        "skill_level_distribution": {},
        "programming_languages_mentioned": [],
        "leadership_claims_summary": {},
        "overall_credibility_assessment": ""
    }
    
    # Collect data from all analyses
    skill_levels = []
    languages = []
    leadership_claims = []
    deception_patterns = []
    
    for analysis in analyses:
        revealed_truth = analysis.get("revealed_truth", {})
        deception_info = analysis.get("deception_patterns", [])
        
        # Collect skill levels
        skill_level = revealed_truth.get("skill_mastery", "unknown")
        if skill_level != "unknown":
            skill_levels.append(skill_level)
        
        # Collect programming languages
        language = revealed_truth.get("programming_language", "")
        if language and language.lower() != "not specified":
            languages.append(language.lower())
        
        # Collect leadership claims
        leadership = revealed_truth.get("leadership_claims", "")
        if leadership:
            leadership_claims.append(leadership)
        
        # Collect deception patterns
        if isinstance(deception_info, list):
            for pattern in deception_info:
                if isinstance(pattern, dict):
                    lie_type = pattern.get("lie_type", "")
                    if lie_type:
                        deception_patterns.append(lie_type)
    
    # Generate skill level distribution
    from collections import Counter
    if skill_levels:
        skill_counter = Counter(skill_levels)
        insights["skill_level_distribution"] = dict(skill_counter)
    
    # Generate language summary
    if languages:
        lang_counter = Counter(languages)
        insights["programming_languages_mentioned"] = list(lang_counter.keys())
    
    # Generate leadership summary
    if leadership_claims:
        leadership_counter = Counter(leadership_claims)
        insights["leadership_claims_summary"] = dict(leadership_counter)
    
    # Generate common deception indicators
    if deception_patterns:
        deception_counter = Counter(deception_patterns)
        insights["common_deception_indicators"] = [
            {"pattern": pattern, "frequency": count} 
            for pattern, count in deception_counter.most_common(5)
        ]
    
    # Generate detected patterns
    patterns = []
    if skill_levels:
        most_common_skill = Counter(skill_levels).most_common(1)[0]
        patterns.append(f"Most common skill level: {most_common_skill[0]} ({most_common_skill[1]} occurrences)")
    
    if languages:
        most_common_lang = Counter(languages).most_common(1)[0]
        patterns.append(f"Most mentioned language: {most_common_lang[0]} ({most_common_lang[1]} occurrences)")
    
    if deception_patterns:
        patterns.append(f"Total deception indicators detected: {len(deception_patterns)}")
    
    insights["detected_patterns"] = patterns
    
    # Generate overall credibility assessment
    total_analyses = len(analyses)
    deception_rate = len(deception_patterns) / total_analyses if total_analyses > 0 else 0
    
    if deception_rate > 0.7:
        credibility = "Low - High frequency of deception indicators detected"
    elif deception_rate > 0.4:
        credibility = "Medium - Moderate deception indicators present"
    elif deception_rate > 0.1:
        credibility = "Good - Few deception indicators detected"
    else:
        credibility = "High - Minimal deception indicators found"
    
    insights["overall_credibility_assessment"] = f"{credibility} (Deception rate: {deception_rate:.1%})"
    
    return insights

if __name__ == "__main__":
    # Directory containing audio files
    audio_directory = "voices/audio"
    
    # Check if directory exists
    if not os.path.exists(audio_directory):
        print(f"❌ Directory not found: {audio_directory}")
        print("Creating sample directory structure...")
        os.makedirs(audio_directory, exist_ok=True)
        print(f"✅ Created directory: {audio_directory}")
        print("Please add audio files to this directory and run again.")
    else:
        print(f"🎯 Processing all audio files from: {audio_directory}")
        
        # Process all audio files
        result, output_file = process_multiple_audio_files(
            audio_directory=audio_directory,
            output_file="comprehensive_truth_weaver_analysis.json"
        )
        
        if result and output_file:
            print(f"\n🎉 Comprehensive analysis completed successfully!")
            print(f"📄 Results saved to: {output_file}")
            
            # Display final summary
            metadata = result.get("metadata", {})
            insights = result.get("consolidated_insights", {})
            
            print(f"\n{'='*60}")
            print("📊 FINAL COMPREHENSIVE SUMMARY")
            print(f"{'='*60}")
            print(f"📁 Files Processed: {metadata.get('total_files_processed', 0)}")
            print(f"👥 Subjects Analyzed: {metadata.get('total_subjects_analyzed', 0)}")
            print(f"⏰ Analysis Time: {metadata.get('analysis_timestamp', 'N/A')}")
            print(f"🎯 Overall Assessment: {insights.get('overall_credibility_assessment', 'N/A')}")
            print(f"🔍 Patterns Detected: {len(insights.get('detected_patterns', []))}")
            print(f"⚠️  Deception Indicators: {len(insights.get('common_deception_indicators', []))}")
            print(f"💻 Languages Found: {', '.join(insights.get('programming_languages_mentioned', ['None']))}")
        else:
            print(f"\n❌ Failed to complete comprehensive analysis")
            print("Please check the audio files and try again.")