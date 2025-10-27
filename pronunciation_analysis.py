import json
import os

def group_by_phone(word_list):
    """
    For a word_list formatted as in SpeechAce's response,
    go through all phones in all words, group by phone name,
    average their scores, and aggregate a unique list of all their 'sound_most_like'.

    Returns:
        [
            {
                "phone": <phone_name>,
                "average_quality_score": <rounded_float>,
                "sounds_most_like": [<list of unique sounds_most_like>]
            },
            ...
        ]
    """
    from collections import defaultdict

    phone_scores = defaultdict(list)
    phone_sounds = defaultdict(set)
    
    for word in word_list:
        for phone in word.get("phone_score_list", []):
            phone_name = phone.get("phone")
            quality_score = phone.get("quality_score", 0)
            sound_most_like = phone.get("sound_most_like")
            if phone_name is None:
                continue
            phone_scores[phone_name].append(quality_score)
            if sound_most_like is not None:
                phone_sounds[phone_name].add(sound_most_like)
    
    phones_data = []
    for phone_name in phone_scores:
        average_score = sum(phone_scores[phone_name]) / len(phone_scores[phone_name])
        phones_data.append({
            "phone": phone_name,
            "average_quality_score": round(average_score),
            "sounds_most_like": sorted(list(phone_sounds[phone_name]))
        })
        
    return phones_data

    

def test_group_by_phone_with_test_results():
        """
        Test the group_by_phone function using 'audio_file/test_results.json'.
        Passes the word_score_list of this json as the word_list argument.
        Prints the grouped phone data.
        """
        json_path = os.path.join("audio_file", "test_results.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Get the word_list from the test_results.json structure
        word_list = (
            data.get("text_score", {}).get("word_score_list", [])
        )

        result = group_by_phone(word_list)
        print("Grouped phones:")
        for phone_data in result:
            print(phone_data)

if __name__ == "__main__":
    test_group_by_phone_with_test_results()