import requests
import json

def get_transcript(video_url, lang_code):
    url = "https://tactiq-apps-prod.tactiq.io/transcript"
    
    payload = {
        "videoUrl": video_url,
        "langCode": lang_code
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
video_url = "https://www.youtube.com/watch?v=5ZogXQ_X_CY"
lang_code = "en"

result = get_transcript(video_url, lang_code)

if result:
    print("Transcript received successfully:")
    print(json.dumps(result, indent=2))
else:
    print("Failed to get transcript.")