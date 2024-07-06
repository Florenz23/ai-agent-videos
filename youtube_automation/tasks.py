from crewai import Task
from textwrap import dedent

class YoutubeAutomationTasks():
    def __init__(self, title_suggestion_amount, title_result_amount):
        self.title_suggestion_amount = title_suggestion_amount
        self.title_result_amount = title_result_amount

    def create_video_suggestions(self, agent, video_topic):
        return Task(
            description=dedent(f"""
                Create potential titles for a given YouTube 
                video topic. Your job is to create {self.title_suggestion_amount} tiles wich are 
                relevant to the given {video_topic} and have the potential to attract viewers and get viral.
                """),
            agent=agent,
            expected_output=dedent(f"""
                - a list of {self.title_suggestion_amount} video titles 
                """),
        )

    def manage_youtube_video_research(self, agent, video_topic):
        return Task(
            description=dedent(f"""
                For a given video title you do a youtube research
                            
                This research list will be used by other agents to help them generate titles 
                               
                Research List Outline:
                - Title of the video
                - View count
                - Days since published
                - Channel subscriber count
                - Video URL
                       
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
                - Channel subscriber count
                - Video URL
                """),
        )

    def improve_video_titles(self, agent, video_topic):
        return Task(
            description=dedent(f"""
                with the given research data you come up with a list youtube titles 
                Take this information into consideration to create even better titles
                The titles should be less than 70 characters 
                and should have a high click-through-rate.
                The suggested video titles should fit the given {video_topic} 
                The title should catch up the style of the research data
                but should be unique and creative, they should not be the same as the research data
                here you can be creative but make sure the titles are relevant to the topic
                the new video titles should only be inspire by the most successful video titles
                be creative in coming up with variations dont stick too close to the original

                1. you write down some reasoning why you think the most successful videos are successful
                2. then you come up with a list of {self.title_result_amount} titles which are inspired 
                    by the most successful videos and following your reasoning

                Here are some example video titles:
                - CrewAI Tutorial for Beginners: Learn How To Use Latest CrewAI Features
                - CrewAI Tutorial: Complete Crash Course for Beginners
                - How To Connect Local LLMs to CrewAI [Ollama, Llama2, Mistral]
                - How to Use CrewAI to Automate Your Workflow
                - CrewAI Tutorial: How to Build a Digital Workforce
                """),
            agent=agent,
            expected_output=dedent(f"""
                - a list of {self.title_result_amount} video titles 
                """)
        )
