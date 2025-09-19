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
            transcription_text (str): The transcribed audio text
            shadow_id (str): Unique identifier for this analysis
            
        Returns:
            dict: Structured analysis in Truth Weaver format
        """
        
        prompt = f"""
        You are "Truth Weaver", an advanced AI system that analyzes speech patterns and content to detect potential deception, skill level assessment, and credibility indicators.

        Analyze the following transcribed audio and provide a detailed analysis in the exact JSON format specified below.

        TRANSCRIBED TEXT:
        "{transcription_text}"

        Please analyze this text for:
        1. Programming experience level (beginner/intermediate/advanced)
        2. Programming languages mentioned or implied
        3. Skill mastery assessment
        4. Leadership claims and their authenticity
        5. Team experience (individual vs team contributor vs leadership)
        6. Any contradictions or inconsistencies
        7. Deception patterns or credibility concerns

        Return your analysis in this EXACT JSON format:
        {{
            "shadow_id": "{shadow_id}",
            "revealed_truth": {{
                "programming_experience": "X-Y years",
                "programming_language": "language_name",
                "skill_mastery": "beginner/intermediate/advanced",
                "leadership_claims": "authentic/fabricated/unclear",
                "team_experience": "individual contributor/team lead/senior leadership",
                "skills_and_other_keywords": ["keyword1", "keyword2", "keyword3"]
            }},
            "deception_patterns": [
                {{
                    "lie_type": "experience_inflation/responsibility_embellishment/skill_exaggeration/other",
                    "contradictory_claims": ["claim1", "claim2"]
                }}
            ]
        }}

        Base your analysis strictly on the content provided. If information is not clearly stated, use "not specified" or "unclear". Be objective and factual in your assessment.
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                json_text = response_text[json_start:json_end].strip()
            elif '{' in response_text and '}' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_text = response_text[json_start:json_end]
            else:
                json_text = response_text
            
            # Parse JSON
            analysis = json.loads(json_text)
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Raw response: {response_text}")
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
                return analysis, output_file
            except Exception as e:
                print(f"❌ Error saving analysis: {e}")
                return analysis, None
        
        return None, None
    
    def _get_fallback_analysis(self, shadow_id, transcription_text):
        """Provide a basic fallback analysis structure"""
        return {
            "shadow_id": shadow_id,
            "revealed_truth": {
                "programming_experience": "analysis_failed",
                "programming_language": "not analyzed",
                "skill_mastery": "unknown",
                "leadership_claims": "not analyzed",
                "team_experience": "not analyzed",
                "skills_and_other_keywords": ["analysis_error"]
            },
            "deception_patterns": [
                {
                    "lie_type": "analysis_unavailable",
                    "contradictory_claims": ["Could not analyze due to technical error"]
                }
            ]
        }

if __name__ == "__main__":
    # Example usage
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