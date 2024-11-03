from swarm import Swarm, Agent
from utils.store_screenshot import store_screenshot
from utils.analyse_image import analyse_start_image
from utils.compare_images import compare_images
import anthropic
from constants import demo_img_path,recent_state_img_path,html_code_path,ini_description_path, recent_state_analysis_path
import os



anthropic_client = anthropic.Anthropic()

client = Swarm()

def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return False
    except IOError as e:
        raise IOError(f"Error reading the file: {e}")

def store_txt(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def call_claude(instruction):
    # Send a message to Claude 3.5 Sonnet
    response = anthropic_client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=8192,
    messages=[
        {"role": "user", "content": instruction}
        ]
    )
    response_text = response.content[0].text
    print(response_text)
    store_txt(html_code_path, response_text)

def ini_session() -> str:
    print("ini session")
    website_description = read_file(ini_description_path)
    if not website_description:
        print("create desciption")
        ini_description= analyse_start_image(demo_img_path)
        store_txt(ini_description_path,ini_description )
        website_description = read_file(ini_description_path)

    # get instructions
    instructions = """you are a senior web developer using only html and css, 
            return plein html and nothing else, 
            write the code for the following website description: 
    """ + website_description
    # generate code 
    print("analyse image")
    call_claude(instructions)
    print("store screenshot")
    store_screenshot(html_code_path, recent_state_img_path)
    return "INI_INSTRUCTIONS"

def write_code(instruction) -> str:
    print("instcutions", instruction)
    # get recent code
    # call clude with instructions
    call_claude(instruction)
    store_screenshot(html_code_path, recent_state_img_path)

def analyse_result() -> str:
    website_description = read_file(ini_description_path)
    image_analysis = compare_images(demo_img_path, recent_state_img_path)
    if not image_analysis:
        return "no_data"
    store_txt(recent_state_analysis_path,image_analysis)
    print(image_analysis)


    recent_code = read_file(html_code_path)

    instructions = """you are a senior web developer using only html and css, 
            dont do mayor changes on the existing code, only improve the parts
            mentioned in the instructions,
            return plein html and nothing else, only return html, nothing else, 
            when using css, include it in the html code
            here is the recent code:  
            """ + recent_code + """
            which is based on the following website description:  
            """ + website_description + """
            consider it too then improve it considering the following instructions:
            """ + image_analysis
    return instructions

agent = Agent(
    name="Agent",
    instructions = (
        "You are an experienced web developer, who is orchestrating the dev process. "
        "First, you call `analyse_result`, then pass the results to `write_code`, "
        "if analyse_result returns 'no_data' only call ini_session"
    ),
    functions=[ini_session, analyse_result, write_code],
)

messages = [{"role": "user", "content": "start"}]

response = client.run(agent=agent, messages=messages)
print(response.messages[-1]["content"])
