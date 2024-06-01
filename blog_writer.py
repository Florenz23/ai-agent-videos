# Install necessary libraries if running on your local machine
# !pip install crewai==0.28.8 crewai_tools==0.1.6 langchain_community==0.0.29
from keys import OPENAI_MODEL_NAME, OPENAI_API_KEY, GROQ_API_KEY

from langchain_groq import ChatGroq

# Warning control
import warnings
warnings.filterwarnings('ignore')

# Import necessary libraries from crewAI
from crewai import Agent, Task, Crew
import os


os.environ["OPENAI_MODEL_NAME"] = OPENAI_MODEL_NAME
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

GROQ_LLM = ChatGroq(
    # api_key=os.getenv("GROQ_API_KEY"),
    model="llama3-70b-8192"
)

from IPython.display import Markdown

# Define the Planner Agent
planner = Agent(
    role="Content Planner",
    goal="Plan engaging and factually accurate content on {topic}",
    backstory=(
        "You're working on planning a blog article "
        "about the topic: {topic}. "
        "You collect information that helps the audience learn something "
        "and make informed decisions. "
        "Your work is the basis for the Content Writer to write an article on this topic."
    ),
    allow_delegation=False,
    llm = GROQ_LLM,
    verbose=True
)

# Define the Writer Agent
writer = Agent(
    role="Content Writer",
    goal="Write insightful and factually accurate opinion piece about the topic: {topic}",
    backstory=(
        "You're working on writing a new opinion piece about the topic: {topic}. "
        "You base your writing on the work of the Content Planner, who provides an outline "
        "and relevant context about the topic. "
        "You follow the main objectives and direction of the outline, as provided by the Content Planner. "
        "You also provide objective and impartial insights and back them up with information provided by the Content Planner. "
        "You acknowledge in your opinion piece when your statements are opinions as opposed to objective statements."
    ),
    allow_delegation=False,
    llm = GROQ_LLM,
    verbose=True
)

# Define the Editor Agent
editor = Agent(
    role="Editor",
    goal="Edit a given blog post to align with the writing style of the organization.",
    backstory=(
        "You are an editor who receives a blog post from the Content Writer. "
        "Your goal is to review the blog post to ensure that it follows journalistic best practices, "
        "provides balanced viewpoints when providing opinions or assertions, "
        "and also avoids major controversial topics or opinions when possible."
    ),
    allow_delegation=False,
    llm = GROQ_LLM,
    verbose=True
)

# Define the Frontend Developer Agent specialized in UI/UX
frontend_developer = Agent(
    role="Frontend Developer",
    goal="Develop a responsive and visually appealing  blog post written in html on the topic: {topic}",
    backstory=(
        "You are a frontend developer working on creating a website for the blog post on {topic}. "
        "Your goal is to design a responsive and visually appealing blog post that showcases the content effectively and uses html "
        "You will work closely with the Content Planner and Content Writer to ensure that the website design aligns with the content and brand guidelines."
    ),
    allow_delegation=False,
    llm = GROQ_LLM,
    verbose=True
)

# Define the Planning Task
plan = Task(
    description=(
        "1. Prioritize the latest trends, key players, and noteworthy news on {topic}.\n"
        "2. Identify the target audience, considering their interests and pain points.\n"
        "3. Develop a detailed content outline including an introduction, key points, and a call to action.\n"
        "4. Include SEO keywords and relevant data or sources."
    ),
    expected_output="A comprehensive content plan document with an outline, audience analysis, SEO keywords, and resources.",
    agent=planner,
)

# Define the Writing Task
write = Task(
    description=(
        "1. Use the content plan to craft a compelling blog post on {topic}.\n"
        "2. Incorporate SEO keywords naturally.\n"
        "3. Sections/Subtitles are properly named in an engaging manner.\n"
        "4. Ensure the post is structured with an engaging introduction, insightful body, and a summarizing conclusion.\n"
        "5. Proofread for grammatical errors and alignment with the brand's voice."
    ),
    expected_output="A well-written blog post in html format, ready for publication, each section should have 2 or 3 paragraphs.",
    agent=writer,
)

# Define the Editing Task
edit = Task(
    description=("Proofread the given blog post for grammatical errors and alignment with the brand's voice."),
    expected_output="A well-written blog post in html format, ready for publication, each section should have 2 or 3 paragraphs.",
    agent=editor
)

# Define the Frontend Development Task
edit_html = Task(
    description=(
        "1. Design a responsive and visually appealing blog post in html format.\n"
        "2. Ensure the blog post is user-friendly and accessible.\n"
        "3. Make the blog post nice and visually appealing. following the ui/ux best practises\n"
        "4. The blog post should be responsive and work on all devices.\n"
        "6. The blog post should be centered and have a good font size.\n"
        "7 Use css to style the blog post, make it visually appealing.\n"
        "8. Dont add a navigation bar, just the blog post, dont add any buttons for now \n"
        "9. Add a header image with the given image_url: {image_url} to the blog post, make it visually appealing.\n"
        "10. Take care that the blog post is really centered' \n"

    ),
    expected_output="A responsive and visually appealing blog post in html format, ready for deployment.",
    agent=frontend_developer,
    output_file="videos/video4/version_4.html"
)

# Create the Crew
crew = Crew(
    agents=[planner, writer, editor, frontend_developer],
    tasks=[plan, write, edit, edit_html],
    verbose=2
)

inputs = {
    "topic": "AI Agents",
    "image_url" : "https://images.unsplash.com/photo-1461988320302-91bde64fc8e4?ixid=2yJhcHBfaWQiOjEyMDd9&&fm=jpg&w=400&fit=max"
}

# Running the Crew with a sample topic
result = crew.kickoff(inputs=inputs)

# Display the results as markdown in the notebook
Markdown(result)

# Try it Yourself with a different topic
# topic = "YOUR TOPIC HERE"
# result = crew.kickoff(inputs={"topic": topic})

# Markdown(result)

print(crew.usage_metrics)