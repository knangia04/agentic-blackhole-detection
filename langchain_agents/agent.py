from langchain.agents import Tool, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType

# ✅ Correct imports from tools.py
from .tools import fetch_data_tool, preprocess_tool, analyze_tool, report_tool

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

# Setup agent
llm = ChatOpenAI(temperature=0)
agent_executor = initialize_agent(
    tools=TOOLS,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

# Interactive run
if __name__ == "__main__":
    query = "Generate a gravitational wave report for GPS event 1126259462 using detectors H1 and L1"
    agent_executor.run(query)
