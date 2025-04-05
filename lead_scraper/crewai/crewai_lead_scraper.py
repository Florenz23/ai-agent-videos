import os
import re
from crewai import Agent, Task, Crew, Process, LLM
from src.workflows.lead_scraper.tools.scraper import scrape_website
from crewai.tools import tool
import asyncio
from dotenv import load_dotenv
import json
import time
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from uuid import uuid4

load_dotenv()

@tool
def extract_content_from_website(url: str) -> str:
    """
    Extracts content from a website
    returns a markdown formatted string with well structured urls 
    """
    print(f"Scraping website: {url}")
    content = asyncio.run(scrape_website(url))
    print(f"Website scraped successfully")
    return content

# Pydantic models to parse the JSON returned by each task

class WebsiteInformation(BaseModel):
    contact_url: Optional[str] = None
    impressum_url: Optional[str] = None
    decision_maker_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    company_industry: Optional[str] = None
    company_products: Optional[List[str]] = None
    content_summary_points: Optional[List[str]] = None

class CrewAiLeadScraper:
    def __init__(self, input_data: Dict[str, Any]):
        """
        Initialize the CrewAiLeadScraper for a single website.
        
        Args:
            input_data: Dictionary containing workflow configuration and input data
        """
        self.input_data = input_data
        self.website_url = input_data["workflow_input_data"]["domain_url"]
        self.product_text = input_data["workflow_input_data"]["product_txt"]
        self.record_id = uuid4()
        
        # Initialize LLM
        self.llm = LLM(
            model=input_data["model"]
        )

    def run(self) -> Dict[str, Any]:
        """
        Run the lead scraper for a single website.
        
        Returns:
            Dictionary with the result data
        """
        print(f"\nProcessing {self.website_url}...")
        
        # Create the scraper agent
        scrape_agent = Agent(
            role='Web Scraper Agent',
            goal='find the required website information',
            backstory="""You are an expert web scraper agent specializing in 
            finding website information""",
            allow_delegation=False,
            tools=[extract_content_from_website],
            llm=self.llm
        )

        # Create the scrape task
        scrape_root_url_task = Task(
            description=f"""
            find the contact information on the root url : {self.website_url}
            """,
            expected_output="a well structured json object",
            agent=scrape_agent,
            output_json=WebsiteInformation
        )

        print(f"Writing email for {self.website_url}")
        
        # Create the email task
        scrape_contact_task = Task(
            description=f"""
            find the contact information based on the impressum_url and the contact_url
            """,
            expected_output="a well structured json object",
            agent=scrape_agent,
            context=[scrape_root_url_task],
            output_json=WebsiteInformation
        )

        # Create and run the crew
        crew = Crew(
            # agents=[scraper_agent, email_writer_agent],
            agents=[scrape_agent],
            tasks=[scrape_root_url_task, scrape_contact_task],
            verbose=False,
            process=Process.sequential
        )

        # Kick off the crew and get the result
        crew_result = crew.kickoff()
        
        print(f"Successfully processed {self.website_url}")
        
        return crew_result

if __name__ == "__main__":
    # Define input data
    new_input_data = {
        "workflow": "lead_scraper",
        "model": "gpt-4o-mini",
        "framework": "crewai",
        "llm_provider": "openai",
        "workflow_input_data": {
            "product_txt": "Custom Wall Art/Canvas Prints",
            "domain_url": "https://www.der-friseur-freiberg.de/"
        }
    }
    
    # Create and run the scraper
    start_time = time.time()
    scraper = CrewAiLeadScraper(input_data=new_input_data)
    result = scraper.run()
    result_json = json.dumps(result.json, indent=4)
    print(f"Result: {result}")
    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")