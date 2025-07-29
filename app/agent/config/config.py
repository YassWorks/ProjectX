from langgraph.checkpoint.memory import MemorySaver
from langchain_cerebras import ChatCerebras
from langgraph.prebuilt import create_react_agent
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import ToolMessage
from langgraph.graph.message import add_messages
# from langgraph.graph import StateGraph, END, START
from app.agent.config.tools import (
    create_wd,
    create_file,
    modify_file,
    delete_file,
    read_file,
    list_directory,
    execute_command,
    execute_code,
    # stall,
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
        # stall,
        append_file,
        delete_directory,
    ]

    mem = MemorySaver()

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
        checkpointer=mem,
        # post_model_hook=invalid_toolcall_checker,
    )

    return agent


def invalid_toolcall_checker(state):
    try:
        ai_message = state["messages"][-1]
        content = ai_message.content
        tool_calls = ai_message.tool_calls
        
        print(ai_message)

        # no tool_calls returned, but looks like it tried to
        if not tool_calls and (
            "{" in content or "<tool_call>" in content or "arguments" in content
        ):
            print('\n'+" YEA IT WAS HERE (IT FUCKED UP) ".center(50,'#')+'\n')

            error_message = ToolMessage(
                tool_call_id="retry",
                content="Error: Your tool call was malformed or non-JSON. Please fix and retry.",
                invalid=True,
            )

            if "messages" not in state:
                state["messages"] = []
            state["messages"].append(error_message)

    except Exception as e:
        print(f"⚠️ post_model_hook failed: {e}")
        
    return state
