from typing import List, Type
from pydantic.v1 import BaseModel, Field
from crewai_tools import BaseTool
import os
import subprocess
import json
import time
from datetime import datetime, timezone

class VideoDetails(BaseModel):
    video_id: str
    title: str
    channel_id: str
    channel_title: str
    days_since_published: int
    view_count: int
    like_count: int
    dislike_count: int
    comment_count: int
    channel_subscriber_count: int

class YoutubeVideoSearchToolInput(BaseModel):
    """Input for YoutubeVideoSearchTool."""
    keyword: str = Field(..., description="The search keyword.")

class YoutubeVideoFullSearchTool(BaseTool):
    name: str = "Search YouTube Videos with Details"
    description: str = "Searches YouTube videos based on a keyword and returns detailed information for each video."
    args_schema: Type[BaseModel] = YoutubeVideoSearchToolInput

    def _run(self, keyword: str, max_results: int = 5) -> List[VideoDetails]:
        api_key = os.getenv("YOUTUBE_API_KEY")
        search_url = "https://www.googleapis.com/youtube/v3/search"
        
        search_command = [
            'curl', '-G', search_url,
            '--data-urlencode', 'part=snippet',
            '--data-urlencode', f'q={keyword}',
            '--data-urlencode', f'maxResults={max_results}',
            '--data-urlencode', 'type=video',
            '--data-urlencode', f'key={api_key}',
            '-H', 'Accept: application/json'
        ]
        
        search_result = subprocess.run(search_command, capture_output=True, text=True)
        
        if search_result.returncode != 0:
            raise Exception(f"curl command failed with exit code {search_result.returncode}: {search_result.stderr}")

        search_items = json.loads(search_result.stdout).get("items", [])
        video_details_list = []

        for item in search_items:
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            channel_id = item["snippet"]["channelId"]
            channel_title = item["snippet"]["channelTitle"]
            publish_date = datetime.fromisoformat(
                item["snippet"]["publishedAt"].replace('Z', '+00:00')).astimezone(timezone.utc)
            days_since_published = (datetime.now(timezone.utc) - publish_date).days

            details_url = "https://www.googleapis.com/youtube/v3/videos"
            details_command = [
                'curl', '-G', details_url,
                '--data-urlencode', 'part=snippet,statistics',
                '--data-urlencode', f'id={video_id}',
                '--data-urlencode', f'key={api_key}',
                '-H', 'Accept: application/json'
            ]
            details_result = subprocess.run(details_command, capture_output=True, text=True)

            if details_result.returncode != 0:
                raise Exception(f"curl command failed with exit code {details_result.returncode}: {details_result.stderr}")

            details_item = json.loads(details_result.stdout).get("items", [])[0]

            view_count = int(details_item["statistics"]["viewCount"])
            like_count = int(details_item["statistics"].get("likeCount", 0))
            dislike_count = int(details_item["statistics"].get("dislikeCount", 0))
            comment_count = int(details_item["statistics"].get("commentCount", 0))

            channel_url = "https://www.googleapis.com/youtube/v3/channels"
            channel_command = [
                'curl', '-G', channel_url,
                '--data-urlencode', 'part=statistics',
                '--data-urlencode', f'id={channel_id}',
                '--data-urlencode', f'key={api_key}',
                '-H', 'Accept: application/json'
            ]
            channel_result = subprocess.run(channel_command, capture_output=True, text=True)

            if channel_result.returncode != 0:
                raise Exception(f"curl command failed with exit code {channel_result.returncode}: {channel_result.stderr}")

            channel_item = json.loads(channel_result.stdout).get("items", [])[0]
            channel_subscriber_count = int(channel_item["statistics"]["subscriberCount"])

            video_details_list.append(VideoDetails(
                video_id=video_id,
                title=title,
                channel_id=channel_id,
                channel_title=channel_title,
                days_since_published=days_since_published,
                view_count=view_count,
                like_count=like_count,
                dislike_count=dislike_count,
                comment_count=comment_count,
                channel_subscriber_count=channel_subscriber_count
            ))

        return video_details_list

if __name__ == "__main__":
    tool = YoutubeVideoFullSearchTool()
    results = tool.run(keyword="Top 10 Most Beautiful Places to Visit in the World", max_results=5)
    for result in results:
        print(result.json(indent=4))
