from crewai import Agent

class YoutubeAutomationAgents():
    def __init__(self, agent_model, title_suggestion_amount, title_result_amount):
        self.agent_model = agent_model
        self.title_suggestion_amount = title_suggestion_amount
        self.title_result_amount = title_result_amount

    def youtube_manager(self):
        return Agent(
            role="YouTube Manager",
            goal=f"""Oversee the process of title creation of youtube videos for a 
            given content topic""",
            backstory=f"""As a methodical and detailed oriented manager, you are responsible 
                for overseeing the preparation of YouTube Video Titles, you take care that the 
                processes does not lead to endless loops and that the titles are relevant to the
                content topic,
                """,
            allow_delegation=True,
            llm = self.agent_model,
            verbose=True,
        )

    def research_manager(self, youtube_video_search_tool):
        return Agent(
            role="YouTube Research Agent",
            goal=f""" your goal is to do precise and focused research on youtube videos,
            """,
            backstory=f""" you are very experienced in the field of youtube video research and you
            decide what data to return to the youtube manager, focus on the data that is relevant,
            """,
            verbose=True,
            allow_delegation=False,
            llm = self.agent_model,
            tools=[youtube_video_search_tool]
        )

    def title_creator(self):
        return Agent(
            role="Title Creator",
            goal=f"""
                You come up with high engaging youtube titles, which will lead to high click through 
                rates
            """,
            backstory=f"""
                you are an experienced title creator, you know how to create titles that are engaging
                and will lead to high click through rates, you are using your experience to create
                titles that are relevant to the content topic
            """,
            llm = self.agent_model,
            allow_delegation=False,
            verbose=True
        )

