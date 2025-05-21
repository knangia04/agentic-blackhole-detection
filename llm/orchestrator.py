from langchain.agents import AgentExecutor
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv
from .agent import detection_agent, detection_tools, llm
from agents.gw_metadata import resolve_event_metadata

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

    metadata = resolve_event_metadata(user_query)

    if metadata:
        # 🌌 Inject parameter context into the prompt
        enrichment = (
            f"\n\nDetected metadata for {metadata.get('gps')}:\n"
            f"- mass1: {metadata.get('mass1')}\n"
            f"- mass2: {metadata.get('mass2')}\n"
            f"- distance: {metadata.get('distance')}\n"
        )
        enriched_query = f"{user_query.strip()}\n\n{enrichment}"
    else:
        enriched_query = user_query

    executor = AgentExecutor(
        agent=detection_agent,
        tools=detection_tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=20,
        max_execution_time=120,
    )

    try:
        result = executor.invoke({"input": enriched_query})
        final_output = result.get("output", "No output generated")
    except Exception as e:
        print(f"Error running agent: {str(e)}")
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