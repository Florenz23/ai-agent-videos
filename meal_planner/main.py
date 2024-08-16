from crewai import Agent, Task, Crew, Process
from crewai_tools import FileReadTool, DirectoryReadTool

from langchain_openai import ChatOpenAI
import agentops

agentops.init(default_tags=["dish_schedule"])

from dotenv import load_dotenv
load_dotenv()

docs_tool = DirectoryReadTool(directory='videos/video_7')
file_tool = FileReadTool()

OpenAIGPT4 = ChatOpenAI(
    model="gpt-4o-2024-08-06"
)

OpenAIGPT4MINI = ChatOpenAI(
    model="gpt-4o-mini"
)

AGENT_MODEL = OpenAIGPT4MINI

dish_scheduler = Agent(
    role="Weekly Dish Planner",
    goal="Generate a weekly dish schedule based on past cooking habits and user preferences.",
    backstory="""You are responsible for ensuring the user has a varied and satisfying meal 
    plan each week, while also considering special requests.""",
    verbose=True,
    allow_delegation=False,
    memory=True,
    llm = AGENT_MODEL,
)

file_reader = Agent(
    role="File Reader",
    goal="read data from files and pass it to the Weekly Dish Planner",
    backstory="""you are responsible to get all the data neeed by the Weekly Dish Planner""",
    verbose=True,
    memory=False,
    allow_delegation=True,
    tools=[docs_tool,file_tool ],
    llm = AGENT_MODEL,
)

read_data = Task(
    description="""Read the dish list from dish_list.txt and last week schedule from 
    last_week_schedule.txt and pass the data to the Weekly Dish Planner.""", 
    expected_output="a string with the data from the files",
    agent=file_reader,
)

generate_schedule_task = Task(
    description=(
        """Based on the provided dish list and last week's schedule, generate a new dish 
        schedule for the next week (7 suggestions in total) that consider  
        the users instruction: {user_instruction}
        Importand: respect the infomation of the labels
        Make sure to check with a human if the draft is good before finalizing your answer."""
    ),
    expected_output=""""
    A tab seperated text containing the schedule for the next week, including the 
    ingredients needed for each dish
    Example Output:
    Montag  Dienstag        Mittwoch        Donnerstag      Freitag Samstag Sonntag
    Bolognese       Nudelsalat      Kürbissuppe     Frühlingsrollen Tuna    Cremesuppe      Lasagne

    Ingredients Needed:

    - Bolognese: 4x tomaten, 2x tüte, 1x sahne, 1x spaghetti, 1x passierte tomaten, 1x reibekäse, wurzeln, 1x Hackfleisch
    - Nudelsalat: 1x Pirelli Nudeln, 1x Salatdressing, Mais, 6x Würstchen, 2x Tomaten, 1x Gurken
    - Kürbissuppe: 1x kürbis, 1x sahne, 1x brühwürfel, 3x kartofflen
    - Frühlingsrollen: 1x Frühlingsrolle
    - Tuna: 1x tuna, 1x saure sahne, 1x spaghetti
    - Cremesuppe: 1x hack, 6x lauchstangen, 2x zwiebeln, 1x sahne schmelzkäse / frischkäse, 1x kräuter schmelzkäse / frischkäse
    - Lasagne: 1x Box Nudelplatten, 3x Paprika, 2x Zwiebeln, 2x Tomaten, 2x Gewürztüten, 1x Hackfleisch, 1x Creme Fraiche
    """,
    agent=dish_scheduler,
    human_input=True
)

generate_shopping_list_task = Task(
    description="""If the user approves the schedule, generate a shopping list based on the 
    ingredients needed for the new schedule, all the ingredients are provided in the dish list.
    dont invent new ingredients, only use the ingredients from the dish list.
   
    """,
    expected_output="""
        a shopping list with the ingredients needed for the new schedule.
        Example output:
        1x Hack
        6x Lauchstangen
        2x Zwiebeln
        1x Sahne Schmelzkäse / Frischkäse
        1x Kräuter Schmelzkäse / Frischkäse
        1x Tuna
        1x Saure Sahne
        1x Spaghetti
        1x Schlagsahne
        6x Würstchen
        1x Eiernudeln
        """,
    agent=dish_scheduler,
)


inputs = {
    "user_instruction": """Create a new dish schedule for the next week, include one special 
        meal that I did not cook yet"""
}

crew = Crew(
    agents=[dish_scheduler],
    tasks=[read_data, generate_schedule_task, generate_shopping_list_task],
    process=Process.sequential
)

result = crew.kickoff(inputs=inputs)

print("######################")
print(result)
print("Crew usage", crew.usage_metrics)
agentops.end_session("Success")