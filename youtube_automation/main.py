from crewai import Crew

from agents import YoutubeAutomationAgents
from tasks import YoutubeAutomationTasks
from langchain_openai import ChatOpenAI
from tools.youtube_video_full_search_tool import YoutubeVideoFullSearchTool
from langchain_groq import ChatGroq


OpenAIGPT4 = ChatOpenAI(
    model="gpt-4o"
)

OpenAIGPT3 = ChatOpenAI(
    model="gpt-3.5-turbo"
)

GROQ_LLM = ChatGroq(
    model="llama3-70b-8192"
)

MANAGER_MODEL = OpenAIGPT4
# MANAGER_MODEL = GROQ_LLM
# MANAGER_MODEL = OpenAIGPT3
AGENT_MODEL = OpenAIGPT4
# AGENT_MODEL = GROQ_LLM
# AGENT_MODEL = OpenAIGPT3

TITLE_SUGGESTION_AMOUNT = 2
TITLE_RESULT_AMOUNT = 10


content_topic = """top ... videos, like: top .. most beautiful ... in the world, 
top ... best ... in the world, top ... most expensive ... in the world"""

agents = YoutubeAutomationAgents(
    agent_model = AGENT_MODEL,
    title_suggestion_amount = TITLE_SUGGESTION_AMOUNT,
    title_result_amount = TITLE_RESULT_AMOUNT
)

youtube_research_tool = YoutubeVideoFullSearchTool()

youtube_manager = agents.youtube_manager()
research_manager = agents.research_manager(
    youtube_research_tool
)

title_creator = agents.title_creator()

tasks = YoutubeAutomationTasks(
    title_suggestion_amount = TITLE_SUGGESTION_AMOUNT,
    title_result_amount = TITLE_RESULT_AMOUNT
)

create_video_suggestions = tasks.create_video_suggestions(
    agent = title_creator,
    video_topic = content_topic
)

manage_youtube_videeo_research = tasks.manage_youtube_video_research(
    agent = research_manager,
    video_topic = content_topic
)

improve_video_titles = tasks.improve_video_titles(
    agent = title_creator,
    video_topic = content_topic
)

crew = Crew(
    agents = [
        youtube_manager,
        research_manager,
        title_creator
    ],
    tasks = [
        create_video_suggestions,
        manage_youtube_videeo_research,
        improve_video_titles
    ],
    manager_llm = MANAGER_MODEL
)

results = crew.kickoff()

print("rew usage: ", crew.usage_metrics)
print("results: ", results)