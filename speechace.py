"""Pronunciation analysis functions for Francoflex."""

import os
import json
import requests
from dotenv import load_dotenv
import openai
import numpy as np
import time

# Optional imports for audio recording (only needed locally, not on server)
try:
    import sounddevice as sd
except ImportError:
    sd = None
try:
    import soundfile as sf
except ImportError:
    sf = None

# Load environment variables
load_dotenv()

def analyze_pronunciation_data(json_data):
    """
    Parse pronunciation API response and extract structured feedback data
    
    Returns:
    - overall_score: Main pronunciation score
    - word_analysis: Detailed breakdown by word with syllables and phones
    """
    
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data
    
    # Extract overall metrics - handle different response structures
    overall_score = None
    
    # Try different possible structures
    if 'speechace_score' in data and 'pronunciation' in data['speechace_score']:
        overall_score = data['speechace_score']['pronunciation']
    elif 'text_score' in data and 'quality_score' in data['text_score']:
        overall_score = data['text_score']['quality_score']
    elif 'text_score' in data and 'word_score_list' in data['text_score']:
        # Calculate average from word scores
        word_scores = [word['quality_score'] for word in data['text_score']['word_score_list']]
        overall_score = sum(word_scores) / len(word_scores) if word_scores else 0
    
    # Process each word
    word_analysis = []
    
    for word_data in data['text_score']['word_score_list']:
        word_info = {
            'word': word_data['word'],
            'quality_score': word_data['quality_score'],
            'syllables': [],
            'phones': []
        }
        
        # Extract syllable data
        for syll in word_data['syllable_score_list']:
            syllable_info = {
                'letters': syll['letters'],
                'quality_score': syll['quality_score'],
                'phone_count': syll['phone_count']
            }
            word_info['syllables'].append(syllable_info)
        
        # Extract phone data with pronunciation issues
        for phone in word_data['phone_score_list']:
            phone_info = {
                'target_phone': phone['phone'],
                'quality_score': phone['quality_score'],
                'sound_most_like': phone.get('sound_most_like'),
                'needs_work': phone['quality_score'] < 70
            }
            word_info['phones'].append(phone_info)
        
        word_analysis.append(word_info)
    
    return {
        'overall_score': overall_score,
        'word_analysis': word_analysis
    }

def get_speechace_response(recording, target_text):
    """
    Make a request to the SpeechAce API using given audio_content (dict).
    Return the SpeechAce API JSON response (or raise on failure).
    `audio_content` should contain:
        {
            'user_audio_file': (filename, fileobj, mimetype),
            'text': target_text
        }
    """
    import os
    import requests

    api_key = os.getenv('SPEECHACE_API_KEY')
    if not api_key:
        raise ValueError("SpeechAce API key not configured")

    url = f"https://api.speechace.co/api/scoring/text/v9/json?key={api_key}&dialect=fr-fr"

    files = {
        'user_audio_file': recording
    }
    data = {
        'text': target_text
    }

    response = requests.post(url, data=data, files=files)
    response.raise_for_status()
    return response.json()

def create_compact_pronunciation_json(json_data):
    """
    Create a compact JSON structure from SpeechAce API response.
    
    Returns a reduced JSON with:
    - speechace_score and cefr_score
    - words with quality_score and phones (phone, quality_score, sound_most_like)
    """
    
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data
    
    # Extract overall scores
    speechace_score = data.get('speechace_score', {})
    cefr_score = data.get('cefr_score', {})
    
    # Process words
    words = []
    if 'text_score' in data and 'word_score_list' in data['text_score']:
        for word_data in data['text_score']['word_score_list']:
            word_info = {
                'word': word_data['word'],
                'quality_score': round(word_data['quality_score'])
            }
            
            # Process phones - create a dictionary with phone as key
            phones = {}
            for phone in word_data['phone_score_list']:
                phone_key = phone['phone']
                phones[phone_key] = {
                    'quality_score': round(phone['quality_score']),
                    'sound_most_like': phone.get('sound_most_like')
                }
            
            word_info['phones'] = phones
            words.append(word_info)
    
    return {
        'speechace_score': speechace_score,
        'cefr_score': cefr_score,
        'words': words
    }

def convert_speechace_to_custom_response(speechace_response):
    """
    Convert SpeechAce API response to custom Francoflex response format.
    
    Args:
        speechace_response: Raw SpeechAce API response (dict or JSON string)
    
    Returns:
        dict: Custom response format with overall_score, word_analysis, and metadata
    """
    
    if isinstance(speechace_response, str):
        data = json.loads(speechace_response)
    else:
        data = speechace_response
    
    # Extract overall pronunciation score from the correct nested location
    overall_score = None
    if 'text_score' in data and 'speechace_score' in data['text_score']:
        speechace_data = data['text_score']['speechace_score']
        if 'pronunciation' in speechace_data:
            overall_score = round(speechace_data['pronunciation'])  # This is an int from 0-100
    elif 'speechace_score' in data and 'pronunciation' in data['speechace_score']:
        overall_score = round(data['speechace_score']['pronunciation'])
    elif 'text_score' in data and 'quality_score' in data['text_score']:
        overall_score = round(data['text_score']['quality_score'])
    
    # Extract CEFR score from the correct nested location
    cefr_score = {}
    if 'text_score' in data and 'cefr_score' in data['text_score']:
        cefr_data = data['text_score']['cefr_score']
        if 'pronunciation' in cefr_data:
            cefr_score['level'] = cefr_data['pronunciation']  # This is a string like "B1", "B2", etc.
    
    # Process word analysis
    word_analysis = []
    if 'text_score' in data and 'word_score_list' in data['text_score']:
        for word_data in data['text_score']['word_score_list']:
            word_info = {
                'word': word_data['word'],
                'quality_score': round(word_data['quality_score']),
                'phones': {}
            }
            
            # Process phones for this word
            for phone in word_data['phone_score_list']:
                phone_key = phone['phone']
                word_info['phones'][phone_key] = {
                    'quality_score': round(phone['quality_score']),
                    'sound_most_like': phone.get('sound_most_like')
                }
            
            word_analysis.append(word_info)
    
    # Create custom response format
    custom_response = {
        'overall_score': overall_score,
        'speechace_score': data.get('speechace_score', {}),
        'cefr_score': cefr_score,
        'word_analysis': word_analysis,
        'metadata': {
            'status': data.get('status', 'unknown'),
            'api_version': 'v9',
            'raw_api_response': data  # Include the complete raw API response
        }
    }
    
    return custom_response

def generate_word_feedback(word_data, overall_score):
    """
    Generate AI-powered cheering message and individualized feedback for a word.
    
    Args:
        word_data: Word analysis data with phones and quality scores
        overall_score: Overall pronunciation score for context
    
    Returns:
        dict: AI feedback with cheering message and specific tips
    """
    
    try:
        # Check if OpenAI API key is available
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            return {
                "cheering_message": "Great effort! Keep practicing!",
                "feedback": "Continue working on your pronunciation."
            }
        
        # Prepare context for the AI
        word = word_data['word']
        word_score = word_data['quality_score']
        phones_data = word_data['phones']
        
        # Create detailed context about the word's pronunciation
        phones_context = []
        for phone, phone_data in phones_data.items():
            quality_score = phone_data['quality_score']
            sound_most_like = phone_data.get('sound_most_like')
            
            phone_info = f"Phone '{phone}': {quality_score}/100"
            if sound_most_like:
                phone_info += f" (sounds like '{sound_most_like}')"
            phones_context.append(phone_info)
        
        phones_text = "; ".join(phones_context)
        
        # Create the prompt for OpenAI
        prompt = f"""
You are a supportive French pronunciation coach for Francoflex. Provide encouraging feedback for this word:

Word: "{word}"
Word Score: {word_score}/100
Overall Pronunciation Score: {overall_score}/100
Phone Details: {phones_text}

Please provide:
1. A short, encouraging cheering message (1-2 sentences, positive and motivating)
2. Specific, actionable feedback for improving this word's pronunciation (focus on the phones that need work)

Respond in JSON format:
{{
    "cheering_message": "your encouraging message here",
    "feedback": "your specific improvement tips here"
}}

Keep it concise, supportive, and focused on the specific pronunciation issues for this word.
"""
        
        # Make API call to OpenAI
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a supportive French pronunciation coach. Always be encouraging and provide specific, actionable feedback."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        # Parse the response
        ai_response = response.choices[0].message.content.strip()
        
        # Try to parse as JSON, fallback if it fails
        try:
            feedback_data = json.loads(ai_response)
            return feedback_data
        except json.JSONDecodeError:
            # Fallback if AI doesn't return valid JSON
            return {
                "cheering_message": "Great effort! Keep practicing!",
                "feedback": ai_response if ai_response else "Continue working on your pronunciation."
            }
            
    except Exception as e:
        # Fallback in case of any error
        return {
            "cheering_message": "Great effort! Keep practicing!",
            "feedback": f"Continue working on your pronunciation. (AI feedback unavailable: {str(e)})"
        }

def add_ai_feedback_to_response(custom_response):
    """
    Add AI-generated feedback to each word in the custom response.
    
    Args:
        custom_response: The custom response format with word_analysis
    
    Returns:
        dict: Updated response with AI feedback for each word
    """
    
    overall_score = custom_response.get('overall_score', 0)
    
    # Add AI feedback to each word
    for word_data in custom_response['word_analysis']:
        ai_feedback = generate_word_feedback(word_data, overall_score)
        word_data['ai_feedback'] = ai_feedback
    
    return custom_response

def print_pronunciation_analysis(parsed_data):
    """Print formatted pronunciation analysis."""
    print("=" * 60)
    print("🎤 PRONUNCIATION ANALYSIS")
    print("=" * 60)
    print(f"Overall Score: {parsed_data['overall_score']}/100")
    print()
    
    print("📝 Word Analysis:")
    for word_data in parsed_data['word_analysis']:
        print(f"\n🔤 {word_data['word']} - {word_data['quality_score']}/100")
        
        print("  Syllables:")
        for syllable in word_data['syllables']:
            print(f"    • {syllable['letters']}: {syllable['quality_score']}/100")
        
        print("  Phones:")
        for phone in word_data['phones']:
            status = "❌" if phone['needs_work'] else "✅"
            print(f"    {status} {phone['target_phone']}: {phone['quality_score']}/100")
            if phone['sound_most_like']:
                print(f"      Sounds like: {phone['sound_most_like']}")

def test_pronunciation_interactive():
    """
    Test function that analyzes pronunciation using a fixed audio file
    and a fixed sentence.
    """
    print("FRANCOFLEX PRONUNCIATION TEST")
    print("=" * 50)
    
    target_text = "Bonjour, comment allez-vous?"
    audio_path = "audio_file/user_test.wav"

    print(f"\nUsing target sentence: {target_text}")
    print(f"Using audio file: {audio_path}")
    
    try:
        # Analyze pronunciation with SpeechAce
        print("\nAnalyzing pronunciation with SpeechAce...")
        with open(audio_path, "rb") as audio_file:
            raw_data = get_speechace_response(audio_file, target_text)
        
        if raw_data:
            raw_response_filename = f"test_results.json"
            raw_response_path = os.path.join("audio_file", raw_response_filename)
            os.makedirs("audio_file", exist_ok=True)
            with open(raw_response_path, 'w', encoding='utf-8') as f:
                json.dump(raw_data, f, indent=2, ensure_ascii=False)
            print(f"Raw SpeechAce response saved to: {raw_response_path}")
        else:
            print(f"Analysis failed: {raw_data}")
            if raw_data:
                print("\nRaw response for debugging:")
                print(json.dumps(raw_data, indent=2))
    except Exception as e:
        print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    # Run the interactive test function
    test_pronunciation_interactive()
