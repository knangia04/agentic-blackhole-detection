import os
from dotenv import load_dotenv
from langchain.agents import Tool, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType

from .tools import fetch_data_tool, preprocess_tool, analyze_tool, report_tool

# Load environment variables
load_dotenv()

# Get API key from environment or set it directly (not recommended for production)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    # Warning: Setting API keys directly in code is not recommended for production
    # Only using this as a fallback if environment variable is not set
    OPENROUTER_API_KEY = "noapikey"  # Replace with your actual key in a .env file instead

# ✅ Define tools with correct references
TOOLS = [
    Tool(
        name="Fetch GW Data",
        func=fetch_data_tool,
        description="Fetch gravitational wave strain data for a given detector and GPS event."
    ),
    Tool(
        name="Preprocess Data",
        func=preprocess_tool,
        description="Preprocess raw strain data for a given detector and GPS event."
    ),
    Tool(
        name="Analyze Signal",
        func=analyze_tool,
        description="Run matched filter and detection for a given detector and GPS event."
    ),
    Tool(
        name="Generate Report",
        func=report_tool,
        description="Run the full pipeline and generate PDF report."
    ),
]

# Setup OpenRouter LLM client
llm = ChatOpenAI(
    model="meta-llama/llama-4-maverick:free",  # OpenRouter model name
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=OPENROUTER_API_KEY,
    temperature=0,
    model_kwargs={
        "extra_headers": {
            "HTTP-Referer": "https://github.com/sidharthanand/agentic-blackhole-detection",
            "X-Title": "Agentic Black Hole Detection",
        }
    }
)

# Setup agent
detection_agent = initialize_agent(
    tools=TOOLS,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

# Export tools for use in orchestrator
detection_tools = TOOLS

# Interactive run
if __name__ == "__main__":
    query = "Generate a gravitational wave report for GPS event 1126259462 using detectors H1 and L1"
    detection_agent.run(query)
