from typing import Annotated, Literal
import os

from autogen import ConversableAgent
from autogen import register_function
import pprint

from dotenv import load_dotenv
load_dotenv()
from autogen import ConversableAgent
from tools.yahoo_finance import yahoo_finance_tool
import time

llm_config = {
    "model": "gpt-4o-mini",
    "cache_seed": None,
    }

start_time = time.time()


def read_file(file_path: str) -> str:
    with open(file_path, "r") as file:
        return file.read()

def write_file(file_path: str, content: str) -> None:
    with open(file_path, "w") as file:
        file.write(content)

# Let's first define the assistant agent that suggests tool calls.
assistant = ConversableAgent(
    name="Assistant",
    system_message="You are a helpful AI assistant. "
    "Return 'TERMINATE' when the task is done.",
    llm_config=llm_config,
)

# The user proxy agent is used for interacting with the assistant agent
# and executes tool calls.
user_proxy = ConversableAgent(
    name="User",
    llm_config = False,
    is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
    human_input_mode="NEVER",
)

# Register the calculator function to the two agents.
register_function(
    yahoo_finance_tool,
    caller=assistant,  # The assistant agent can suggest calls to the calculator.
    executor=user_proxy,  # The user proxy agent can execute the calculator calls.
    name="yahoo_finance_tool",  # By default, the function name is used as the tool name.
    description="Input: Ticker symbol of a stock, it will return stock data",  # A description of the tool.
)

# Register the read_file function to the two agents.
register_function(
    read_file,
    caller=assistant,  # The assistant agent can suggest calls to the read_file function.
    executor=user_proxy,  # The user proxy agent can execute the read_file calls.
    name="read_file",  # By default, the function name is used as the tool name.
    description="Read a file",  # A description of the tool.
)

# Register the write_file function to the two agents.
register_function(
    write_file,
    caller=assistant,  # The assistant agent can suggest calls to the write_file function.
    executor=user_proxy,  # The user proxy agent can execute the write_file calls.
    name="write_file",  # By default, the function name is used as the tool name.
    description="Write to a file",  # A description of the tool.
)

ticker_symbol = "AAPL"

user_message = f"""
        description:
        first for a given ticker: {ticker_symbol} fetch the data using the yahoo_finance_tool 
        then get warren buffett's investment principles by opening
        the file 
        workflows/stock_analysis/warren_buffet_investement_principles.txt
        then you provide a comprehensive analysis of the ticker
        write short and concise the pros why warren buffett would invest in
        this company and the cons why he wouldn't
        then summarize the company evaluation and provide a recommendation
        then you give a warren buffet buy recomendation from 0 to 10 (10 is best)
        finally write the result to the file 
        workflows/stock_analysis/stock_analysis_autogen/stock_analysis.txt
        expected_output:
        - Pros why Warren Buffett would invest in this company
        - Cons why Warren Buffett wouldn't invest in this company
        - Company Evaluation Summary
        - Warren Buffet Buy Recommendation
    """

chat_result = user_proxy.initiate_chat(assistant, message=user_message)

pprint.pprint(chat_result.cost)
#print needed time
print("--- %s seconds ---" % (time.time() - start_time))


