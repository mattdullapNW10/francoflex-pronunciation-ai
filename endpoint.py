def analyze_pronunciation(audio_url, target_text, lv1,lv2,user_id):
    audio = get_audio(audio_url)
    speechace_response = get_speechace_response(audio, target_text)

