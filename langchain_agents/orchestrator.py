from langchain.agents import AgentExecutor
from langchain_core.runnables import RunnableConfig
from .agent import detection_agent, detection_tools


def run_orchestration(user_query: str):
    """
    Run the full agent orchestration for gravitational wave detection.

    Args:
        user_query (str): Natural language query from the user.

    Returns:
        str: Agent's final answer or reasoning trace.
    """
    executor = AgentExecutor(
        agent=detection_agent,
        tools=detection_tools,
        verbose=True,  # Logs each step of agent thought process
        return_intermediate_steps=True
    )

    config = RunnableConfig(tags=["agent", "gw-detection"])

    result = executor.invoke({"input": user_query}, config=config)

    final_output = result.get("output")
    print("\n[Agent Response]\n", final_output)
    return final_output


if __name__ == "__main__":
    print("🤖 Ask a question about gravitational wave detection:")
    query = input("> ")
    run_orchestration(query)