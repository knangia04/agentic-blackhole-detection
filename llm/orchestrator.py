from langchain.agents import AgentExecutor
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv
from .agent import detection_agent, detection_tools, llm

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
    # Create the agent executor with the correct setup for newer LangChain versions
    executor = AgentExecutor(
        agent=detection_agent,
        tools=detection_tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=20,
        max_execution_time=120
    )

    # Run the executor with the user's query using the newer invoke method
    try:
        result = executor.invoke({"input": user_query})
        final_output = result.get("output", "No output generated")
    except Exception as e:
        print(f"Error running agent: {str(e)}")
        # Fallback if the agent execution fails
        response = llm.invoke([HumanMessage(content=f"""
        I need to analyze gravitational wave data related to the following query:
        
        {user_query}
        
        Due to technical limitations, I'll provide a direct answer without using tools:
        """)]) 
        final_output = response.content

    print("\n[Agent Response]\n", final_output)
    return final_output


if __name__ == "__main__":
    print("🤖 Ask a question about gravitational wave detection:")
    query = input("> ")
    run_orchestration(query)