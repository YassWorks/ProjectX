from langgraph.checkpoint.memory import MemorySaver
from langchain_cerebras import ChatCerebras
from langgraph.prebuilt import create_react_agent
from langgraph.graph.state import CompiledStateGraph
from app.agent.config.tools import (
    create_wd,
    create_file,
    modify_file,
    delete_file,
    read_file,
    list_directory,
    execute_command,
    execute_code,
    stall,
    append_file,
    delete_directory,
)


def get_agent(
    model_name: str,
    api_key: str,
    system_prompt: str | None = None,
) -> CompiledStateGraph:
    """Load configuration and initialize the code generator agent."""

    llm = ChatCerebras(
        model=model_name,
        temperature=1.5,
        timeout=None,
        max_retries=5,
        api_key=api_key,
    )

    tools = [
        create_wd,
        create_file,
        modify_file,
        delete_file,
        read_file,
        list_directory,
        execute_command,
        execute_code,
        stall,
        append_file,
        delete_directory,
    ]

    mem = MemorySaver()

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
        checkpointer=mem,
    )

    return agent
