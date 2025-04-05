from typing import Dict, Any, List, Optional
import os
import sys
import time
from dotenv import load_dotenv
import asyncio
from uuid import uuid4
import json
import re
import dotenv
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))
dotenv.load_dotenv()

load_dotenv()

# Add the project root to the Python path

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from src.workflows.lead_scraper.tools.scraper import scrape_website
from autogen_agentchat.teams import RoundRobinGroupChat
from pydantic import BaseModel
from autogen_core.tools import FunctionTool

class WebsiteInformation(BaseModel):
    decision_maker_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    impressum_url: Optional[str] = None
    company_industry: Optional[str] = None
    contact_url: Optional[str] = None
    company_products: Optional[List[str]] = None
    content_summary_points: Optional[List[str]] = None


async def scrape_website_tool(url: str) -> str:
        """Get the content from a website URL."""
        print(f"Scraping website: {url}")
        content = await scrape_website(url)
        print(f"Website scraped successfully")
        return content


class AutogenLeadScraper:
    def __init__(self, input_data: Dict[str, Any]):
        """
        Initialize the AutogenLeadScraper for a single website.
        
        Args:
            input_data: Dictionary containing workflow configuration and input data
        """
        self.input_data = input_data
        self.website_url = input_data["workflow_input_data"]["domain_url"]
        self.record_id = uuid4()
        
        # Initialize the model client

    
    def parse_json_response(self, response_content):
        """Parse JSON response from the agent."""
        # Extract JSON string from the response if needed
        json_match = re.search(r'```json\s*(.*?)\s*```', response_content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response_content
        
        try:
            response_dict = json.loads(json_str)
            return response_dict
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            print(f"Raw content: {response_content}")
            return {}
            
    async def run(self) -> Dict[str, Any]:
        """
        Run the lead scraper for a single website and return the result.
        
        Returns:
            The Autogen chat result object, potentially augmented with execution time.
        """

        product_text = self.input_data["workflow_input_data"]["product_txt"]

        model_client_scraper = OpenAIChatCompletionClient(
            model=self.input_data["model"],
            response_format=WebsiteInformation
        )

        web_search_tool = FunctionTool(
            scrape_website_tool,
            description="Search the web for information",
            strict=True
        )

        # Create the assistant agent with tools
        scrape_agent_root_url = AssistantAgent(
            name="lead_scraper_assistant_root_url",
            system_message="""You are an expert web scraper agent specializing in 
            find the contact information on the root url
            """,
            description="""
            """,
            model_client=model_client_scraper,
            tools=[web_search_tool],
            reflect_on_tool_use=True,
        )
        scrape_agent_contact = AssistantAgent(
            name="lead_scraper_assistant_contact",
            system_message="""You are an expert web scraper agent specializing in 
            you use the impressum_url and the contact_url to find all required contact information
            """,
            description="""
            """,
            model_client=model_client_scraper,
            tools=[web_search_tool],
            reflect_on_tool_use=True,
        )

        # Create the task message
        # task = f"""Return me the email data for the url: {self.website_url}:
        #         """
        task = f"""find me all necessary website information for the url: {self.website_url} 
                """

        # team = RoundRobinGroupChat([scrape_ragent, email_writer_agent], max_turns=2)
        # team = RoundRobinGroupChat([scrape_agent_root_url, scrape_agent_impressum], max_turns=2)
        team = RoundRobinGroupChat([scrape_agent_root_url, scrape_agent_contact], max_turns=2)
        
        # Record start time
        start_time = time.time()

        result = await team.run(task=task)

        # Record end time
        end_time = time.time()
        execution_time_seconds = end_time - start_time

        # Attach execution time to the result object
        # Assuming the result object allows adding arbitrary attributes
        try:
            setattr(result, 'execution_time_seconds', execution_time_seconds)
        except AttributeError:
            # As a fallback, maybe add it to the summary dict if it exists?
            if hasattr(result, 'summary') and isinstance(result.summary, dict):
                result.summary['execution_time_seconds'] = execution_time_seconds

        return result

if __name__ == "__main__":
    # Define input data
    new_input_data = {
        "workflow": "lead_scraper",
        "model": "gpt-4o-mini",
        "framework": "autogen",
        "llm_provider": "openai",
        "workflow_input_data": {
            "product_txt": "Custom Wall Art/Canvas Prints",
            # "domain_url": "https://www.der-friseur-freiberg.de/impressum.php"
            # "domain_url": "https://www.der-friseur-freiberg.de/"
            "domain_url": "https://rang-und-namen.de/"
            # "domain_url": "https://www.themarfaspirit.com/"
        }
    }
    
    # Create and run the scraper
    start_time = time.time()
    scraper = AutogenLeadScraper(input_data=new_input_data)
    result = asyncio.run(scraper.run())
    last_message = result.messages[-1]
    result_json = last_message.content
    messages = result.messages
    prompt_tokens = 0
    completion_tokens = 0
    
    # Extract token usage from all messages
    for message in messages:
        if hasattr(message, 'models_usage') and message.models_usage:
            usage = message.models_usage
            if isinstance(usage, dict):
                completion_tokens += usage.get('completion_tokens', 0)
                recent_completion_tokens = usage.get('completion_tokens', 0)
                prompt_tokens += usage.get('prompt_tokens', 0)
                recent_prompt_tokens = usage.get('prompt_tokens', 0)
            elif hasattr(usage, 'completion_tokens') and hasattr(usage, 'prompt_tokens'):
                completion_tokens += usage.completion_tokens
                prompt_tokens += usage.prompt_tokens
    
    website_url = new_input_data["workflow_input_data"]["domain_url"]
    print(f"Prompt tokens: {prompt_tokens}")
    print(f"Completion tokens: {completion_tokens}")
    print(f"Successfully processed {website_url}")
    print(result_json)
    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")
