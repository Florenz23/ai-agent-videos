from crewai import Task
from textwrap import dedent

class TranscriptResearchTasks():
    def __init__(self):
        pass

    def do_youtube_video_research(self, agent, tool, search_query):
        return Task(
            description=dedent(f"""
                For a the given search_query: {search_query} you do research on YouTube

                the results of the research will be passed to the next agent
                            
                Research List Outline:
                - Title of the video
                - View count
                - Days since published
                - Like count
                - Video URL
                - Video Id
                       
                Important Notes: 
                - Make sure the final Research List Outline doesn't contain duplicate titles
                - It is SUPER IMPORTANT that you only populate the research list with real YouTube videos 
                    and YouTube URLs that actually link to the YouTube Video.
                """),
            agent=agent,
            expected_output=dedent(f"""
                Full list which includes the following data:
                - Title of the video
                - View count
                - Days since published
                - Like count
                - Video URL
                - Video Id
                """),
            tools=[tool]
        )

    def pick_best_result(self, agent, search_query):
        return Task(
            description=dedent(f"""
                you are provided with a list of youtube video research data,
                pick the best video to get insights from
                the video should be the most relevant to the search query: {search_query} 
                and have good youtube metrics like view count, days since published and like count 
                relative to the other videos in the list,
                when you made your choice its not necceesary to do further research on the video
                just return the title and video id of the best video
                and pass it to the next agent
                """),
            agent=agent,
            expected_output=dedent(f"""
                - title and video id of the best video 
                """)
        )

    def get_top_insights(self, agent, tool):
        return Task(
            description=dedent(f"""
                first get the transcript of the given video by passing the video id 
                to the youtube video transcrip reader tool
                then you extract the top 5 insights from the transcript.
                """),
            agent=agent,
            tools=[tool],
            expected_output=dedent(f"""
                - bullet list of top 5 insights 
                """)
        )