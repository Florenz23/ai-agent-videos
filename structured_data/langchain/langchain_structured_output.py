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

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate

# Import Yahoo Finance tool
from src.tools.tool_yahoo_finance import get_stock_data

# Load environment variables
load_dotenv()

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
    key: str = Field(description="Name of the KPI")
    rating: int = Field(description="Rating from 0-10, where 10 is best")

class InvestmentAnalysis(BaseModel):
    reasoning: str = Field(description="Detailed reasoning for the investment decision based on Warren Buffett's principles")
    rating: int = Field(description="Overall investment rating from 0-10, where 10 is best")
    relevant_kpis: List[RelevantKPI] = Field(description="List of relevant KPIs with individual ratings")
    improvement_requirements: str = Field(description="Areas where the company needs to improve")

class LangchainStructuredOutput:
    def __init__(self, input_data: Dict[str, Any]):
        """
        Initialize the LangchainStructuredOutput for a stock analysis.
        
        Args:
            input_data: Dictionary containing workflow configuration and input data
        """
        self.input_data = input_data
        self.ticker = input_data["workflow_input_data"]["ticker"]
        self.record_id = uuid4()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=input_data["model"]
        )
        
        # Set up tools
        self.tools = [analyze_stock]
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def run(self) -> Dict[str, Any]:
        """
        Run the stock analysis based on Warren Buffett's principles.
        
        Returns:
            Dictionary with the analysis results
        """
        print(f"\nAnalyzing stock: {self.ticker}...")
        
        # Create the prompt
        template = f"""You are an expert investment analyst who follows Warren Buffett's 
        investment principles to evaluate stocks. You believe in value investing and 
        long-term perspectives.
        
        Here are Warren Buffett's investment principles:
        {warren_buffett_principles}
        
        Please analyze the stock with ticker {{ticker}} based on Warren Buffett's investment principles.
        Use the analyze_stock tool to retrieve the financial data for this stock.
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # Create initial message
        messages = [HumanMessage(content=prompt.format(ticker=self.ticker))]
        
        # First invocation: Model decides which tools to call
        ai_msg = self.llm_with_tools.invoke(messages)
        messages.append(ai_msg)
        
        # Process tool calls and collect results
        tool_outputs = []
        if ai_msg.tool_calls:
            for tool_call in ai_msg.tool_calls:
                if tool_call["name"].lower() == "analyze_stock":
                    tool_output = analyze_stock.invoke(tool_call["args"]["ticker"])
                    tool_outputs.append(
                        ToolMessage(content=str(tool_output), tool_call_id=tool_call["id"])
                    )
        
        # Append tool results to message history
        messages.extend(tool_outputs)
        
        # Add a final prompt to produce structured output
        final_prompt = """
        Based on the stock data and Warren Buffett's principles, please provide a structured 
        investment analysis then return clearly structured JSON response. 
        Rating is between 0 and 10, where 10 is best.
        """
        
        messages.append(HumanMessage(content=final_prompt))
        
        # Use structured output for final analysis
        structured_llm = self.llm.with_structured_output(InvestmentAnalysis)
        final_response = structured_llm.invoke(messages)
        
        print(f"Successfully analyzed {self.ticker}")
        
        # Convert to dictionary for consistency with CrewAI output
        return final_response.dict()

if __name__ == "__main__":
    # Define input data
    new_input_data = {
        "workflow": "structured_data",
        "model": "gpt-4o-mini",
        "framework": "langchain",
        "llm_provider": "openai",
        "workflow_input_data": {
            "ticker": "AAPL"
        }
    }
    
    # Create and run the stock analyzer
    start_time = time.time()
    analyzer = LangchainStructuredOutput(input_data=new_input_data)
    result = analyzer.run()
    
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
