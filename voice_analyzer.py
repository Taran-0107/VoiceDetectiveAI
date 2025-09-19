import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VoiceAnalyzer:
    def __init__(self):
        """Initialize the Voice Analyzer with Gemini AI"""
        api_key = os.getenv('GEMINI_API')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp')
    
    def analyze_transcription(self, transcription_text, shadow_id="anonymous"):
        """
        Analyze transcribed audio text and return structured analysis
        
        Args:
            transcription_text (str): The transcribed audio text from all sessions
            shadow_id (str): Unique identifier for this analysis
            
        Returns:
            dict: Structured analysis in Truth Weaver format
        """
        
        prompt = f"""
        You are "Truth Weaver," an AI Detective specializing in the "Whispering Shadows" case. Your mission is to analyze testimonies and weave together the most likely truth from conflicting accounts.

        **CASE CONTEXT:**
        The subject is a "Whispering Shadow" who has undergone five "truth sessions." Their testimony progresses from confident lies in early sessions to desperate admissions and emotional breakdowns in later ones. Your task is to see through the deception and synthesize the actual truth. Do not just report the last thing said; analyze the entire progression.

        **INSTRUCTIONS:**
        1.  **Synthesize, Don't Just Extract:** Determine the most plausible truth based on all statements. For example, if a subject claims "6 years experience" then later admits "it was an internship," the revealed truth is beginner-level, not 6 years.
        2.  **Infer Details:** Use context to infer information. If a subject mentions specific frameworks like Django or technologies like Kubernetes, list them. If their description of a senior role matches that of a junior, reflect this in the skill mastery assessment.
        3.  **Identify Contradictions:** Pinpoint direct contradictions between claims made across the sessions. These are the key to uncovering deception patterns.

        **TRANSCRIBED TEXT (ALL SESSIONS):**
        "{transcription_text}"

        **REQUIRED JSON OUTPUT FORMAT:**
        Provide your final analysis in this EXACT JSON structure. Populate each field based on your synthesized findings.

        {{
            "shadow_id": "{shadow_id}",
            "revealed_truth": {{
                "programming_experience": "Synthesize the most likely experience range (e.g., '1-2 years', 'less than 1 year').",
                "programming_language": "List the primary language, infer if necessary (e.g., 'Python' if Django is mentioned). Use 'not specified' if truly unknown.",
                "skill_mastery": "Assess the true mastery ('beginner', 'intermediate', 'advanced') based on the evidence, not just their claims.",
                "leadership_claims": "Label as 'authentic', 'exaggerated', 'fabricated', or 'unclear'.",
                "team_experience": "Determine their actual role ('individual contributor', 'team member', 'team lead').",
                "skills_and_other_keywords": ["List specific technologies, skills, or important keywords mentioned."]
            }},
            "deception_patterns": [
                {{
                    "lie_type": "Choose from 'experience_inflation', 'responsibility_embellishment', 'skill_exaggeration', 'fabricated'.",
                    "contradictory_claims": ["Provide a list of direct quotes that contradict each other."]
                }}
            ]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.rfind('```')
                json_text = response_text[json_start:json_end].strip()
            elif '{' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_text = response_text[json_start:json_end]
            else:
                raise json.JSONDecodeError("No JSON object found in response", response_text, 0)

            analysis = json.loads(json_text)
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Raw response received: {response_text}")
            return self._get_fallback_analysis(shadow_id, transcription_text)
        
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            return self._get_fallback_analysis(shadow_id, transcription_text)
    
    def analyze_and_save(self, transcription_text, shadow_id="anonymous", output_file="truth_weaver_analysis.json"):
        """
        Analyze transcription and save to file
        
        Args:
            transcription_text (str): The transcribed audio text
            shadow_id (str): Unique identifier for this analysis
            output_file (str): Output filename
            
        Returns:
            tuple: (analysis_dict, file_path) or (None, None) if failed
        """
        analysis = self.analyze_transcription(transcription_text, shadow_id)
        
        if analysis:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(analysis, f, indent=2, ensure_ascii=False)
                # MODIFICATION: Corrected the undefined variable 'file_path' to 'output_file'
                return analysis, output_file
            except Exception as e:
                print(f"❌ Error saving analysis: {e}")
                return analysis, None
        
        return None, None
    
    def _get_fallback_analysis(self, shadow_id, transcription_text):
        """Provide a basic fallback analysis structure"""
        return {
            "shadow_id": shadow_id,
            "revealed_truth": { "error": "Analysis failed due to a technical error." },
            "deception_patterns": []
        }

if __name__ == "__main__":
    analyzer = VoiceAnalyzer()
    
    sample_text = """Funny thing, when I was seven, I made a boat out of mismatched toys and it sort of held together. 
    Not that it matters, but building that way stuck with me, quick fixes, duct tape elegance. So, when people ask 
    about ownership of systems, I say I built parts of things, stitched services together, and occasionally owned 
    a small feature. Sometimes I talk about entire projects, because it's simpler to tell a story than to read the 
    commit history. It gets messy."""
    
    analysis, file_path = analyzer.analyze_and_save(sample_text, "phoenix_2024")
    
    if file_path:
        print(f"✅ Analysis saved to: {file_path}")
        print("\n📊 Analysis Preview:")
        print(json.dumps(analysis, indent=2))
    else:
        print("❌ Failed to save analysis")