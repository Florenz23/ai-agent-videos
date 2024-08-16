from crewai import Crew

from agents import TranscriptResearchAgents
from tasks import TranscriptResearchTasks
from langchain_openai import ChatOpenAI
from tools.youtube_video_full_search_tool import YoutubeVideoFullSearchTool
from tools.youtuve_video_transcrip_reader_tool import YoutubeVideoTranscripReaderTool

import agentops

from dotenv import load_dotenv
load_dotenv()

agentops.init(default_tags=["transcript_research"])

OpenAIGPT4 = ChatOpenAI(
    model="gpt-4o-2024-08-06"
)

OpenAIGPT4MINI = ChatOpenAI(
    model="gpt-4o-mini"
)

# MANAGER_MODEL = OpenAIGPT4
MANAGER_MODEL = OpenAIGPT4MINI

# AGENT_MODEL = OpenAIGPT4
AGENT_MODEL = OpenAIGPT4MINI

search_query = """how to earn money with pinterest?""" 

youtube_video_full_search_tool = YoutubeVideoFullSearchTool()
youtube_video_transcrip_reader_tool = YoutubeVideoTranscripReaderTool()

agents = TranscriptResearchAgents(AGENT_MODEL)
tasks = TranscriptResearchTasks()

insight_manager = agents.insight_manager()

youtube_full_search_tool = YoutubeVideoFullSearchTool()

research_manager = agents.research_manager()


do_youtube_video_research = tasks.do_youtube_video_research(
    tool=youtube_video_full_search_tool,
    agent=research_manager,
    search_query=search_query,
)

pick_best_result = tasks.pick_best_result(
    agent=insight_manager,
    search_query=search_query
)

get_top_insights = tasks.get_top_insights(
    agent=insight_manager,
    tool = youtube_video_transcrip_reader_tool
)

# Create a new Crew instance
crew = Crew(
    agents=[insight_manager,
            research_manager,
            ],
    tasks=[
        do_youtube_video_research,
        pick_best_result,
        get_top_insights
           ],
    manager_llm=MANAGER_MODEL
)

results = crew.kickoff()

print("Crew usage", crew.usage_metrics)

print("Crew work results:")
print(results)

agentops.end_session('Success')