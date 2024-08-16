import subprocess
import json

def get_youtube_transcript(video_url, format=True):
    url = "https://api.kome.ai/api/tools/youtube-transcripts"
    
    payload = json.dumps({
        "video_id": video_url,
        "format": format
    })
    
    curl_command = [
        'curl', '-X', 'POST', url,
        '-H', 'Content-Type: application/json',
        '-d', payload
    ]
    
    try:
        result = subprocess.run(curl_command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"curl command failed with exit code {result.returncode}: {result.stderr}")
        
        return json.loads(result.stdout)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
video_url = "https://www.youtube.com/watch?v=F8NKVhkZZWI"
format_transcript = True

result = get_youtube_transcript(video_url, format_transcript)

if result:
    print("Transcript received successfully:")
    print(json.dumps(result, indent=2))
else:
    print("Failed to get transcript.")