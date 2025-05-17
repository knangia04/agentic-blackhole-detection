from langchain.agents import AgentExecutor
from langchain_core.runnables import RunnableConfig
from .agent import detection_agent, detection_tools
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_orchestration(user_query: str):
    """
    Run the full agent orchestration for gravitational wave detection.

    Args:
        user_query (str): Natural language query from the user.

    Returns:
        str: Agent's final answer or reasoning trace.
    """
    # Create the agent executor without the agent parameter
    executor = AgentExecutor.from_agent_and_tools(
        agent=detection_agent,
        tools=detection_tools,
        verbose=True,
        return_intermediate_steps=True
    )

    # Run the executor with the user's query
    try:
        # For LangChain >=0.0.267
        result = executor.invoke({"input": user_query})
    except TypeError:
        # Fallback for older LangChain versions
        result = executor.run(user_query)
        return result

    final_output = result.get("output", "No output generated")
    print("\n[Agent Response]\n", final_output)
    return final_output


if __name__ == "__main__":
    print("🤖 Ask a question about gravitational wave detection:")
    query = input("> ")
    run_orchestration(query)