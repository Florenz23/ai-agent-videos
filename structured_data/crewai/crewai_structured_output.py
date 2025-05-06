import os
import re
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
import asyncio
from dotenv import load_dotenv
import json
import time
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from uuid import uuid4
load_dotenv()

# Import Yahoo Finance tool
from src.tools.tool_yahoo_finance import get_stock_data

# Read Warren Buffett investment principles
with open('src/workflows/structured_data/warren_buffet_investement_principles.txt', 'r') as file:
    warren_buffett_principles = file.read()

@tool
def analyze_stock(ticker: str) -> str:
    """
    Retrieves financial data for a stock using Yahoo Finance API
    """
    print(f"Using tool to retrieve stock data for: {ticker}")
    stock_data = get_stock_data(ticker)
    print(f"Stock data retrieved for {ticker}")
    return "\n".join(stock_data)

# Pydantic models to parse the JSON returned by each task
class RelevantKPI(BaseModel):
    key: str
    rating: int

class InvestmentAnalysis(BaseModel):
    reasoning: str
    rating: int  # 0-10, 10 is best
    relevant_kpis: List[RelevantKPI]
    improvement_requirements: str

class CrewAiStructuredOutput:
    def __init__(self, input_data: Dict[str, Any]):
        """
        Initialize the CrewAiStructuredData for a stock analysis.
        
        Args:
            input_data: Dictionary containing workflow configuration and input data
        """
        self.input_data = input_data
        self.ticker = input_data["workflow_input_data"]["ticker"]
        self.record_id = uuid4()
        
        # Initialize LLM
        self.llm = LLM(
            model=input_data["model"]
        )

    def run(self) -> Dict[str, Any]:
        """
        Run the stock analysis based on Warren Buffett's principles.
        
        Returns:
            Dictionary with the analysis results
        """
        print(f"\nAnalyzing stock: {self.ticker}...")
        
        # Create the stock analyst agent
        stock_analyst = Agent(
            role='Investment Analyst',
            goal='Analyze stocks using Warren Buffett\'s investment principles',
            backstory=f"""You are an expert investment analyst who follows Warren Buffett's 
            investment principles to evaluate stocks. You believe in value investing and 
            long-term perspectives. 
            
            Here are Warren Buffett's investment principles:
            {warren_buffett_principles}""",
            allow_delegation=False,
            tools=[analyze_stock],
            llm=self.llm
        )

        # Create the analysis task
        stock_analysis_task = Task(
            description=f"""
            Analyze the stock with ticker {self.ticker} based on Warren Buffett's investment principles.
            Retrieve the financial data using the analyze_stock tool then return clearly structured JSON
            response. Rating is between 0 and 10, where 10 is best.
            """,
            expected_output="A well-structured investment analysis in JSON format",
            agent=stock_analyst,
            output_json=InvestmentAnalysis
        )

        # Create and run the crew
        crew = Crew(
            agents=[stock_analyst],
            tasks=[stock_analysis_task],
            verbose=False,
            process=Process.sequential
        )

        # Kick off the crew and get the result
        crew_result = crew.kickoff()
        
        print(f"Successfully analyzed {self.ticker}")
        
        return crew_result

if __name__ == "__main__":
    # Define input data
    new_input_data = {
        "workflow": "structured_data",
        "model": "gpt-4o-mini",
        "framework": "crewai",
        "llm_provider": "openai",
        "workflow_input_data": {
            "ticker": "AAPL"
        }
    }
    
    # Create and run the stock analyzer
    start_time = time.time()
    analyzer = CrewAiStructuredOutput(input_data=new_input_data)
    result = analyzer.run()
    
    # Get the result data and ensure it's properly parsed
    if isinstance(result.json, str):
        data = json.loads(result.json)
    else:
        data = result.json
    
    # Print JSON version
    result_json = json.dumps(data, indent=4)
    print(f"\nJSON Result:\n{result_json}")
    
    # Print human-readable version
    print("\n" + "="*50)
    print(f"INVESTMENT ANALYSIS FOR {new_input_data['workflow_input_data']['ticker']}")
    print("="*50)
    
    print("\n📝 REASONING:")
    print(data['reasoning'])
    
    print(f"\n⭐ OVERALL RATING: {data['rating']}/10")
    
    print("\n📊 RELEVANT KPIs:")
    for kpi in data['relevant_kpis']:
        print(f"  • {kpi['key']}: {kpi['rating']}/10")
    
    print("\n🔍 IMPROVEMENT REQUIREMENTS:")
    print(data['improvement_requirements'])
    
    print("\n" + "="*50)
    
    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")
