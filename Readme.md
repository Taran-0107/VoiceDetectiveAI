# 🕵️ VoiceDetectiveAI: The Truth Weaver

Welcome, Digital Detective! **VoiceDetectiveAI** is an AI-powered tool designed to solve the _Whispering Shadows Mystery_. It acts as the legendary _Truth Weaver_—an AI so powerful it can untangle webs of lies and extract pure truth from corrupted voice testimonies.

The system transcribes audio sessions and then intelligently analyzes the content to spot contradictions, assess credibility, and synthesize the most likely truth.

---

## ✨ Features

- **Audio Transcription**: Converts audio files (`.mp3`, `.wav`, etc.) into text.
- **Intelligent Analysis**: Uses a language model to analyze the full context of conversations, not just keywords.
- **Deception Detection**: Identifies contradictions and deception patterns across multiple testimony sessions.
- **Structured Output**: Produces a clean JSON file with the revealed truth and an organized transcript file.

---

## ⚙️ How It Works

The project runs in **two phases**:

1. **Transcription Phase**

   - `main.py` processes every audio file in `voices/audio`.
   - Each file is transcribed individually.
   - All transcripts are saved in `transcripts.txt`.

2. **Analysis Phase**
   - Transcripts are grouped by subject (_“shadow”_).
   - Each subject’s complete testimony is sent to the _Truth Weaver_ AI.
   - A holistic analysis is generated and saved in `final_analysis.json`.

---

## 🛠️ Setup and Installation

### Prerequisites

- **Python 3.8+**
- **Git**

### Step 1: Clone the Repository

```bash
git clone https://github.com/Taran-0107/VoiceDetectiveAI.git
cd VoiceDetectiveAI
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Your API Key

The analysis requires a **Google Gemini API key**.

1. Create a `.env` file in the project root.
2. Add your key in the following format:
   ```env
   GEMINI_API="your_api_key"
   ```

---

## 🚀 Running the Analysis

1. Place your audio files in the `voices/audio` directory.
2. Run the script:
   ```bash
   python main.py
   ```

Outputs will be saved in the project’s root directory.

---

## 📄 Output Files

1. **`transcripts.txt`** – Raw transcription of each audio file.  
   Example:

   ```text
   atlas_2025_1.mp3
   I'm a seasoned DevOps engineer specializing in Kubernetes...

   atlas_2025_2.mp3
   Why Calico? Huh, what else would you use...
   ```

2. **`final_analysis.json`** – Structured AI analysis with contradictions flagged.  
   Example:
   ```json
   [
     {
       "shadow_id": "phoenix_2024",
       "revealed_truth": {
         "programming_experience": "3-4 years",
         "programming_language": "python",
         "skill_mastery": "intermediate",
         "leadership_claims": "fabricated",
         "team_experience": "individual contributor",
         "skills_and_other_keywords": ["Machine Learning", "debugging"]
       },
       "deception_patterns": [
         {
           "lie_type": "experience_inflation",
           "contradictory_claims": [
             "I've mastered Python for 6 years",
             "Actually... crackle... maybe 3 years?"
           ]
         }
       ]
     }
   ]
   ```

**🕵️‍♂️ Step into the shadows, unravel the lies, and let the Truth Weaver guide you.**
