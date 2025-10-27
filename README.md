# Francoflex Pronunciation API

A Python API for analyzing French pronunciation using SpeechAce API and OpenAI LLM for detailed feedback.

## 🚀 Features

- 🎤 **Audio Recording**: Record and analyze pronunciation from audio files
- 🎯 **SpeechAce Integration**: Professional pronunciation scoring
- 🤖 **AI-Powered Feedback**: Detailed feedback using OpenAI GPT models
- 📊 **Detailed Analysis**: Word, syllable, and phone-level analysis
- 🎙️ **Microphone Recording**: Test function to record and analyze pronunciation

## 📁 Project Structure

```
pronunciation_api/
├── speechace.py              # SpeechAce API integration and analysis
├── pronunciation_analysis.py # Analysis functions and feedback generation
├── prompts.py                # Langfuse prompts integration
├── endpoint.py               # API endpoint definitions
├── agent.py                  # Agent functionality
├── user.py                   # User-related functions
├── record_audio.py           # Audio recording utilities
├── audio_file/               # Audio files and test results
└── test.json                 # Test data
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8+
- OpenAI API Key
- SpeechAce API Key
- Langfuse API Keys

### Setup

1. Clone the repository:
```bash
git clone https://github.com/mattdullapNW10/francoflex-pronunciation-ai.git
cd francoflex-pronunciation-ai
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install openai langchain-openai langfuse python-dotenv requests pandas sounddevice soundfile numpy
```

4. Create `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
SPEECHACE_API_KEY=your_speechace_api_key_here
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
```

## 📖 Usage

### Recording Audio

Use the `record_audio.py` module to record audio:
```bash
python record_audio.py
```

### Analyzing Pronunciation

```python
from speechace import get_speechace_response

# Analyze pronunciation from audio file
with open("audio_file/user_test.wav", "rb") as audio:
    target_text = "Bonjour, comment allez-vous?"
    result = get_speechace_response(audio, target_text)
    
# Convert to custom format
from speechace import convert_speechace_to_custom_response
custom_result = convert_speechace_to_custom_response(result)

# Add AI feedback
from speechace import add_ai_feedback_to_response
result_with_feedback = add_ai_feedback_to_response(custom_result)
```

## 🎯 API Structure

### SpeechAce Analysis

The `speechace.py` module provides:
- `get_speechace_response()` - Call SpeechAce API
- `analyze_pronunciation_data()` - Parse API response
- `convert_speechace_to_custom_response()` - Convert to custom format
- `add_ai_feedback_to_response()` - Add AI-generated feedback

### Pronunciation Analysis

The `pronunciation_analysis.py` module provides:
- `group_by_phone()` - Group phone scores across words

### Langfuse Integration

The `prompts.py` module provides:
- `generate_pair_exercice()` - Generate pronunciation exercises
- `run_langfuse_prompt()` - Execute Langfuse prompts

## 🔧 Development

Run the test function:
```bash
python speechace.py
```

Or run specific analysis:
```bash
python pronunciation_analysis.py
```

## 🆘 Support

For issues and questions:
- Open an issue on [GitHub](https://github.com/mattdullapNW10/francoflex-pronunciation-ai/issues)

## 🙏 Acknowledgments

- [SpeechAce](https://www.speechace.com/) for pronunciation analysis
- [OpenAI](https://openai.com/) for AI-powered feedback
- [Langfuse](https://langfuse.com/) for prompt management
