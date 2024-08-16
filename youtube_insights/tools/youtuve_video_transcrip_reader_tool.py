from typing import Type
from crewai_tools import BaseTool
from pydantic.v1 import BaseModel, Field
import subprocess
import json

class TranscribeVideoToolInput(BaseModel):
    """Input for TranscribeVideoTool."""
    video_id: str = Field(..., description="The ID or full URL of the YouTube video.")

class YoutubeVideoTranscripReaderTool(BaseTool):
    name: str = "Transcribe YouTube Video"
    description: str = "Transcribes the audio of a YouTube video and returns the subtitles text."
    args_schema: Type[BaseModel] = TranscribeVideoToolInput

    def _run(self, video_id: str) -> str:
        # Check if video_id is a full URL or just an ID
        if not video_id.startswith("http"):
            video_id = f"https://www.youtube.com/watch?v={video_id}"

        # API endpoint
        api_url = "https://api.kome.ai/api/tools/youtube-transcripts"

        # Payload
        payload = json.dumps({
            "video_id": video_id,
            "format": True
        })

        # Construct curl command
        curl_command = [
            'curl', '-X', 'POST', api_url,
            '-H', 'Content-Type: application/json',
            '-d', payload
        ]

        try:
            # Execute curl command
            result = subprocess.run(curl_command, capture_output=True, text=True)
            
            # Check if the command was successful
            if result.returncode != 0:
                raise Exception(f"curl command failed with exit code {result.returncode}: {result.stderr}")

            # Parse the JSON response
            response_data = json.loads(result.stdout)

            # Extract and return the transcript
            if 'transcript' in response_data:
                return response_data['transcript']
            else:
                return "No transcript found in the response."

        except Exception as e:
            return f"An error occurred: {e}"

if __name__ == "__main__":
    tool = YoutubeVideoTranscripReaderTool()
    result = tool.run(video_id="pxiP-HJLCx0")
    print(result)