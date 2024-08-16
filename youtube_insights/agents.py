from crewai import Agent

class TranscriptResearchAgents():
    def __init__(self, agent_model):
        self.agent_model = agent_model

    def insight_manager(self):
        return Agent(
            role="Insight Manager",
            goal=f"""Supervise the process of gaining insights. 
            The goal is to have 5 top insights at the end""",
            backstory=f"""As a methodical and detailed oriented manager, you are responsible 
                for supervising the insights from youtube video transcripts, you take care that the 
                processes does not lead to endless loops and that the insights are relevant to the
                users query,
                """,
            allow_delegation=True,
            llm = self.agent_model,
            verbose=True,
        )

    def research_manager(self):
        return Agent(
            role="YouTube Research Agent",
            goal=f""" your goal is to do precise and focused research on youtube videos,
            """,
            backstory=f""" you are very experienced in the field of youtube video research and you
            decide what data to return to the youtube manager, focus on the data that is relevant,
            """,
            verbose=True,
            allow_delegation=False,
            llm = self.agent_model
        )