# langchain_agents/agent.py

import os
from dotenv import load_dotenv
from langchain.tools import StructuredTool
from langchain.agents import create_react_agent, AgentExecutor
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

from llm.tools import (
    fetch_data_tool, preprocess_tool, analyze_tool, generate_report_tool,
    FetchInput, PreprocessInput, AnalyzeInput, ReportInput
)

# Load Environment & API

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found")

# Define Tools

from langchain.agents import Tool

TOOLS = [
    Tool(
        name="fetch_data_tool",
        func=fetch_data_tool,
        description="Fetch raw gravitational wave data. Input must include 'detector' and 'gps_event'. Example: {'detector': 'H1', 'gps_event': 1135136350}"
    ),
    Tool(
        name="preprocess_tool",
        func=preprocess_tool,
        description="Preprocess raw strain data for the given detector and time."
    ),
    Tool(
        name="analyze_tool",
        func=analyze_tool,
        description="Run matched filter and get SNR peak. Input must include 'detector' and 'gps_time'."
    ),
    Tool(
        name="generate_report_tool",
        func=generate_report_tool,
        description="Generate a PDF report. Input: {'gps_event': 1126259462}"
    ),
]

# LLM Configuration

llm = ChatOpenAI(
    model="mistralai/mistral-small-3.1-24b-instruct:free",
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

# Prompt Template

AGENT_PROMPT = """You are an expert in gravitational wave physics and data analysis.
You help scientists analyze gravitational wave data from LIGO and Virgo detectors.
You can use tools to help with the analysis.

Many analysis tools (such as matched filtering) require an accurate gravitational waveform model, which is defined by the physical parameters of the source system. These include:
- `mass1`: mass of the primary black hole (in solar masses)
- `mass2`: mass of the secondary black hole (in solar masses)
- `distance`: luminosity distance to the source (in megaparsecs)

You must determine these parameters from the question or event name if possible.

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action, as a native Python dictionary (e.g., {{"detector": "H1", "gps_event": 1135136350}})
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Only include **Final Answer** after you are done taking actions, and no further tool calls are needed. Never include both an Action and a Final Answer at the same time.
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
{agent_scratchpad}"""

# Create Agent

detection_agent = create_react_agent(
    llm=llm,
    tools=TOOLS,
    prompt=PromptTemplate.from_template(AGENT_PROMPT),
)

detection_tools = TOOLS