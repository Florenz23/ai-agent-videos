import os
import re
import json
import time
import sys
import asyncio
from typing import Dict, Any, List, Optional
from uuid import uuid4
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
sys.path.insert(0, project_root)

# AutoGen imports
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.tools import FunctionTool

# Import Yahoo Finance tool
from src.tools.tool_yahoo_finance import get_stock_data

# Load environment variables
load_dotenv()

# Read Warren Buffett investment principles
with open('src/workflows/structured_data/warren_buffet_investement_principles.txt', 'r') as file:
    warren_buffett_principles = file.read()

# Define the tool function
async def analyze_stock_async(ticker: str) -> str:
    """
    Retrieves financial data for a stock using Yahoo Finance API
    """
    print(f"Using tool to retrieve stock data for: {ticker}")
    stock_data = get_stock_data(ticker)
    print(f"Stock data retrieved for {ticker}")
    return "\n".join(stock_data)

# Pydantic models for structured output
class RelevantKPI(BaseModel):
    key: str = Field(description="Name of the KPI")
    rating: int = Field(description="Rating from 0-10, where 10 is best")

class InvestmentAnalysis(BaseModel):
    reasoning: str = Field(description="Detailed reasoning for the investment decision based on Warren Buffett's principles")
    rating: int = Field(description="Overall investment rating from 0-10, where 10 is best")
    relevant_kpis: List[RelevantKPI] = Field(description="List of relevant KPIs with individual ratings")
    improvement_requirements: str = Field(description="Areas where the company needs to improve")

class AutogenStructuredOutput:
    def __init__(self, input_data: Dict[str, Any]):
        """
        Initialize the AutogenStructuredOutput for a stock analysis.
        
        Args:
            input_data: Dictionary containing workflow configuration and input data
        """
        self.input_data = input_data
        self.ticker = input_data["workflow_input_data"]["ticker"]
        self.record_id = uuid4()
        
        self.model = input_data["model"]
        
        # Create the stock analysis tool
        self.analyze_stock_tool = FunctionTool(
            analyze_stock_async,
            description="Retrieve financial data for a stock using Yahoo Finance API",
            strict=True
        )

    async def run(self) -> Dict[str, Any]:
        """
        Run the stock analysis based on Warren Buffett's principles.
        
        Returns:
            Dictionary with the analysis results
        """
        print(f"\nAnalyzing stock: {self.ticker}...")
        
        # Create an OpenAI model client with structured output
        model_client = OpenAIChatCompletionClient(
            model=self.model,
            response_format=InvestmentAnalysis,
        )
        
        # Create a single agent that handles both analysis and structured output
        analyst = AssistantAgent(
            name="investment_analyst",
            description="An investment analyst who follows Warren Buffett's principles",
            model_client=model_client,
            system_message=f"""You are an expert investment analyst who follows Warren Buffett's 
            investment principles to evaluate stocks. You believe in value investing and 
            long-term perspectives.
            
            Here are Warren Buffett's investment principles:
            {warren_buffett_principles}
            
            Your task is to analyze the stock with ticker {self.ticker} based on Warren Buffett's investment principles.
            Use the analyze_stock tool to retrieve the financial data for this stock.
            
            After analyzing the stock, provide a structured investment analysis that includes:
            1. Detailed reasoning for your investment decision based on Warren Buffett's principles
            2. Overall investment rating from 0-10, where 10 is best
            3. List of relevant KPIs with individual ratings from 0-10
            4. Areas where the company needs to improve
            
            Format your response following the InvestmentAnalysis schema strictly.
            """,
            tools=[self.analyze_stock_tool],
            reflect_on_tool_use=True,
        )
        
        # Create a message to send to the agent
        message = TextMessage(
            content=f"Analyze {self.ticker} stock and provide a structured investment analysis based on Warren Buffett's principles.",
            source="user"
        )
        
        # Send the message to the agent and get the response
        response = await analyst.on_messages(
            [message],
            cancellation_token=CancellationToken(),
        )
        
        # Get the message content
        final_content = response.chat_message.content
        
        try:
            # Parse the content as JSON directly
            analysis_dict = json.loads(final_content)
            print(f"\nStructured Output Demonstration:")
            print(f"✅ Successfully received structured JSON output for {self.ticker}")
            
            # Print structure validation to show it's properly structured
            print(f"🔍 Output contains expected fields:")
            print(f"  • reasoning: {'✓' if 'reasoning' in analysis_dict else '✗'}")
            print(f"  • rating: {'✓' if 'rating' in analysis_dict else '✗'}")
            print(f"  • relevant_kpis: {'✓' if 'relevant_kpis' in analysis_dict else '✗'}")
            print(f"  • improvement_requirements: {'✓' if 'improvement_requirements' in analysis_dict else '✗'}")
            
            return analysis_dict
        except Exception as e:
            # If direct parsing fails, try to extract JSON from the message
            print(f"Failed to parse structured output directly: {e}")
            try:
                # Try to extract JSON from text if it's embedded
                json_match = re.search(r'```json\s*(.*?)\s*```', final_content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    parsed_data = json.loads(json_str)
                    print(f"Successfully extracted and analyzed JSON for {self.ticker}")
                    return parsed_data
            except Exception as json_error:
                print(f"Failed to extract JSON: {json_error}")
        
        # Fallback if no valid response
        print(f"Failed to get structured analysis for {self.ticker}")
        return {
            "reasoning": "Analysis failed",
            "rating": 0,
            "relevant_kpis": [],
            "improvement_requirements": "Unable to complete analysis"
        }

    def sync_run(self) -> Dict[str, Any]:
        """
        Synchronous wrapper for the run method.
        """
        return asyncio.run(self.run())

if __name__ == "__main__":
    # Define input data
    new_input_data = {
        "workflow": "structured_data",
        "model": "gpt-4o-mini",
        "framework": "autogen",
        "llm_provider": "openai",
        "workflow_input_data": {
            "ticker": "AAPL"
        }
    }
    
    # Create and run the stock analyzer
    start_time = time.time()
    analyzer = AutogenStructuredOutput(input_data=new_input_data)
    result = analyzer.sync_run()
    
    # Print JSON version
    result_json = json.dumps(result, indent=4)
    print(f"\nJSON Result:\n{result_json}")
    
    # Print human-readable version
    print("\n" + "="*50)
    print(f"INVESTMENT ANALYSIS FOR {new_input_data['workflow_input_data']['ticker']}")
    print("="*50)
    
    print("\n📝 REASONING:")
    print(result['reasoning'])
    
    print(f"\n⭐ OVERALL RATING: {result['rating']}/10")
    
    print("\n📊 RELEVANT KPIs:")
    for kpi in result['relevant_kpis']:
        print(f"  • {kpi['key']}: {kpi['rating']}/10")
    
    print("\n🔍 IMPROVEMENT REQUIREMENTS:")
    print(result['improvement_requirements'])
    
    print("\n" + "="*50)
    
    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")
