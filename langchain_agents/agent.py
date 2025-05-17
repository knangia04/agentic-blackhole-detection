import os
from dotenv import load_dotenv
from langchain.agents import Tool, create_react_agent
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor

from .tools import fetch_data_tool, preprocess_tool, analyze_tool, report_tool

# Load environment variables
load_dotenv()

# Get API key from environment
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables")

# Define tools
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

# Setup OpenRouter LLM client with the updated API
llm = ChatOpenAI(
    model="meta-llama/llama-4-maverick:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    temperature=0,
    model_kwargs={
        "extra_headers": {
            "HTTP-Referer": "https://github.com/sidharthanand/agentic-blackhole-detection",
            "X-Title": "Agentic Black Hole Detection",
        }
    }
)

# Custom prompt for the agent
AGENT_PROMPT = """You are an expert in gravitational wave physics and data analysis.
You help scientists analyze gravitational wave data from LIGO and Virgo detectors.
You can use tools to help with the analysis.

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
{agent_scratchpad}"""

# Create agent with tools
detection_agent = create_react_agent(
    llm=llm,
    tools=TOOLS,
    prompt=PromptTemplate.from_template(AGENT_PROMPT)
)

# Export tools for use in orchestrator
detection_tools = TOOLS

# Interactive run
if __name__ == "__main__":
    query = "Generate a gravitational wave report for GPS event 1126259462 using detectors H1 and L1"
    agent_executor = AgentExecutor(agent=detection_agent, tools=TOOLS, verbose=True)
    result = agent_executor.invoke({"input": query})
    print(result["output"])
