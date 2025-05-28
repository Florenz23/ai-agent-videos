import os
import re
import json
import time
import sys
from typing import Dict, Any, List, Optional
from uuid import uuid4
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
sys.path.insert(0, project_root)

# OpenAI Agents imports
import asyncio
from agents import Agent, Runner, function_tool

# Import Yahoo Finance tool
from src.tools.tool_yahoo_finance import get_stock_data

# Load environment variables
load_dotenv()

# Read Warren Buffett investment principles
with open('src/workflows/structured_output/warren_buffet_investement_principles.txt', 'r') as file:
    warren_buffett_principles = file.read()

# Pydantic models to parse the structured output
class RelevantKPI(BaseModel):
    key: str = Field(description="Name of the KPI")
    rating: int = Field(description="Rating from 0-10, where 10 is best")

class InvestmentAnalysis(BaseModel):
    reasoning: str = Field(description="Detailed reasoning for the investment decision based on Warren Buffett's principles")
    rating: int = Field(description="Overall investment rating from 0-10, where 10 is best")
    relevant_kpis: List[RelevantKPI] = Field(description="List of relevant KPIs with individual ratings")
    improvement_requirements: str = Field(description="Areas where the company needs to improve")

class OpenaiAgentsStructuredOutput:
    def __init__(self, input_data: Dict[str, Any]):
        """
        Initialize the OpenaiAgentsStructuredOutput for a stock analysis.
        
        Args:
            input_data: Dictionary containing workflow configuration and input data
        """
        self.input_data = input_data
        self.ticker = input_data["workflow_input_data"]["ticker"]
        self.record_id = uuid4()
        
        # Create the analyze_stock tool function
        @function_tool
        def analyze_stock(ticker: str) -> str:
            """
            Retrieves financial data for a stock using Yahoo Finance API
            
            Args:
                ticker: The stock ticker symbol (e.g. 'AAPL')
            
            Returns:
                A string containing key financial metrics for the stock
            """
            print(f"Using tool to retrieve stock data for: {ticker}")
            stock_data = get_stock_data(ticker)
            print(f"Stock data retrieved for {ticker}")
            return "\n".join(stock_data)
        
        # Set up the agent with the instructions and tools
        self.stock_analyzer = Agent(
            name="Investment Analyst",
            instructions=f"""You are an expert investment analyst who follows Warren Buffett's 
            investment principles to evaluate stocks. You believe in value investing and 
            long-term perspectives.
            
            Here are Warren Buffett's investment principles:
            {warren_buffett_principles}
            
            Analyze the stock ticker provided by the user based on Warren Buffett's principles.
            Use the analyze_stock tool to retrieve financial data for the stock.
            Your final response should be a structured JSON object following the InvestmentAnalysis schema.
            """,
            tools=[analyze_stock],
            output_type=InvestmentAnalysis,
        )

    async def run(self) -> Dict[str, Any]:
        """
        Run the stock analysis based on Warren Buffett's principles.
        
        Returns:
            The full result object containing token usage and structured output
        """
        print(f"\nAnalyzing stock: {self.ticker}...")
        
        # Run the agent with a prompt
        prompt = f"Please analyze the stock with ticker {self.ticker} based on Warren Buffett's investment principles. Retrieve the stock data using the analyze_stock tool."
        
        result = await Runner.run(self.stock_analyzer, input=prompt)
        
        print(f"Successfully analyzed {self.ticker}")
        
        # Return the full result object to capture token usage information
        return result

if __name__ == "__main__":
    # Define input data
    new_input_data = {
        "workflow": "structured_output",
        "model": "gpt-4.1-nano",
        # "model": "gpt-4.1-mini",
        "framework": "openai_agents",
        "llm_provider": "openai",
        "workflow_input_data": {
            "ticker": "AAPL"
        }
    }
    
    # Create and run the stock analyzer
    start_time = time.time()
    
    analyzer = OpenaiAgentsStructuredOutput(input_data=new_input_data)
    result = asyncio.run(analyzer.run())
    
    # Print JSON version
    result_json = result.final_output.model_dump()
    print(f"\nJSON Result:\n{result_json}")
    
    # Print human-readable version
    print("\n" + "="*50)
    print(f"INVESTMENT ANALYSIS FOR {new_input_data['workflow_input_data']['ticker']}")
    print("="*50)
    
    print("\n📝 REASONING:")
    print(result.final_output.reasoning)
    
    print(f"\n⭐ OVERALL RATING: {result.final_output.rating}/10")
    
    print("\n📊 RELEVANT KPIs:")
    for kpi in result.final_output.relevant_kpis:
        print(f"  • {kpi.key}: {kpi.rating}/10")
    
    print("\n🔍 IMPROVEMENT REQUIREMENTS:")
    print(result.final_output.improvement_requirements)
    
    print("\n" + "="*50)
    
    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")
