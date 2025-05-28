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

# Pydantic AI imports
from pydantic_ai import Agent, RunContext

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

class StockAnalyzerDependencies:
    """Dependencies for the stock analyzer agent"""
    def __init__(self, ticker: str):
        self.ticker = ticker

class PydanticStructuredOutput:
    def __init__(self, input_data: Dict[str, Any]):
        """
        Initialize the PydanticStructuredOutput for a stock analysis.
        
        Args:
            input_data: Dictionary containing workflow configuration and input data
        """
        self.input_data = input_data
        
        # Make sure workflow_input_data exists and has expected structure
        if not input_data.get("workflow_input_data"):
            raise ValueError("Missing workflow_input_data in input")
            
        # Get ticker from input data with fallback to AAPL
        self.ticker = input_data.get("workflow_input_data", {}).get("ticker", "AAPL")
        self.record_id = uuid4()
        
        # Get LLM provider or default to 'openai'
        llm_provider = input_data.get("llm_provider", "openai")
        model = input_data.get("model", "gpt-4o-mini")
        
        # Initialize the Pydantic AI agent
        self.stock_analyzer = Agent(
            f"{llm_provider}:{model}",
            deps_type=StockAnalyzerDependencies,
            output_type=InvestmentAnalysis,
            system_prompt=f"""You are an expert investment analyst who follows Warren Buffett's 
            investment principles to evaluate stocks. You believe in value investing and 
            long-term perspectives.
            
            Here are Warren Buffett's investment principles:
            {warren_buffett_principles}
            """
        )
        
        # Register tools
        @self.stock_analyzer.tool
        async def analyze_stock(ctx: RunContext[StockAnalyzerDependencies]) -> str:
            """
            Retrieves financial data for a stock using Yahoo Finance API
            """
            print(f"Using tool to retrieve stock data for: {ctx.deps.ticker}")
            stock_data = get_stock_data(ctx.deps.ticker)
            print(f"Stock data retrieved for {ctx.deps.ticker}")
            return "\n".join(stock_data)

    async def run(self) -> Dict[str, Any]:
        """
        Run the stock analysis based on Warren Buffett's principles.
        
        Returns:
            Dictionary with the analysis results
        """
        try:
            print(f"\nAnalyzing stock: {self.ticker}...")
            
            # Create dependencies
            deps = StockAnalyzerDependencies(ticker=self.ticker)
            
            # Run the agent
            prompt = f"Please analyze the stock with ticker {self.ticker} based on Warren Buffett's investment principles. Use the analyze_stock tool to retrieve the financial data, then provide a structured investment analysis."
            
            result = await self.stock_analyzer.run(prompt, deps=deps)
            
            print(f"Successfully analyzed {self.ticker}")
            
            # Return the result object directly so the parser can extract token usage
            return result
        except Exception as e:
            print(f"Error analyzing stock {self.ticker}: {str(e)}")
            # Return error in a format that can be properly handled
            return {"error": f"Failed to analyze stock: {str(e)}"}

if __name__ == "__main__":
    # Define input data
    new_input_data = {
        "workflow": "structured_output",
        # "model": "gpt-4o-mini",
        "model": "gpt-4.1-nano",
        "framework": "pydantic_agents",
        "llm_provider": "openai",
        "workflow_input_data": {
            "ticker": "AAPL"
        }
    }
    
    # Create and run the stock analyzer
    start_time = time.time()
    
    import asyncio
    analyzer = PydanticStructuredOutput(input_data=new_input_data)
    result = asyncio.run(analyzer.run())
    
    if isinstance(result, dict) and "error" in result:
        print(f"Error: {result['error']}")
    else:
        try:
            # Use model_dump() instead of dict() for Pydantic v2 compatibility
            result_dict = result.output.model_dump() if hasattr(result.output, 'model_dump') else result.output.dict()
            
            # Print human-readable version
            print("\n" + "="*50)
            print(f"INVESTMENT ANALYSIS FOR {new_input_data['workflow_input_data']['ticker']}")
            print("="*50)
            
            print("\n📝 REASONING:")
            print(result_dict['reasoning'])
            
            print(f"\n⭐ OVERALL RATING: {result_dict['rating']}/10")
            
            print("\n📊 RELEVANT KPIs:")
            for kpi in result_dict['relevant_kpis']:
                print(f"  • {kpi['key']}: {kpi['rating']}/10")
            
            print("\n🔍 IMPROVEMENT REQUIREMENTS:")
            print(result_dict['improvement_requirements'])
            
            # Print token usage
            if hasattr(result, 'usage'):
                usage = result.usage()
                print("\n📊 TOKEN USAGE:")
                print(f"  • Request tokens: {usage.request_tokens}")
                print(f"  • Response tokens: {usage.response_tokens}")
                print(f"  • Total tokens: {usage.total_tokens}")
            
            print("\n" + "="*50)
        except Exception as e:
            print(f"Error processing result: {str(e)}")
    
    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")
