from langchain_groq import ChatGroq
import warnings
warnings.filterwarnings('ignore')
from crewai import Agent, Task, Crew
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_LLM = ChatGroq(
    model="llama3-70b-8192"
)

# os.environ["OPENAI_MODEL_NAME"] = 'gpt-3.5-turbo'
os.environ["OPENAI_MODEL_NAME"] = 'gpt-4o'

teacher = Agent(
    role="second grade teacher",
    goal="guide the student to the right answer",
    backstory=(
        "you help the student to figure out the right answer \n"
        "you give little hints \n"
        "you give very short answers, which are maxium 1 sentence long \n"
    ),
    allow_delegation=True,
    # llm = GROQ_LLM,
    verbose=True,
)

student = Agent(
    role="second grade student",
    goal="guess the right answer of the teacher",
    backstory=(
        "you are trying to guess the right answer of the question of the teacher \n"
        "your answer is only one word or one number long \n"
    ),
    allow_delegation=False,
    # llm = GROQ_LLM,
    verbose=True,
)

ask_question = Task(
    description=(
        "let the student guess a number between 1 and 10 \n"
        "the number for the student to guess is 8 \n"
        "if the student guesses 8, the taks is done"
    ),
    expected_output=(
        "instuctions for the student \n"
    ),
    agent= teacher
)

answer_question = Task(
    description=(
        "answer the questions of the teacher \n"
        "follow the instructions of the teacher \n"
    ),
    expected_output="a number between 1 and 10",
    agent= student
)

crew = Crew(
    agents=[teacher, student],
    tasks=[ask_question, answer_question],
    verbose=2,
    memory=True
)


result = crew.kickoff()
print(crew.usage_metrics)


# try without memory
# try with memory 
# try with delegation
# try without delegation 
# bring in two students, one only answers 0-10 other 11-20 coordinator has to 
# figure out that