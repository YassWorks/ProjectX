from langchain_cerebras import ChatCerebras
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import ToolMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END, START
from typing import TypedDict, Annotated
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate
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


class State(TypedDict):
    messages: Annotated[list, add_messages]


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

    template = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt or "You are a helpful assistant."),
            ("human", "{messages}"),
        ]
    )

    llm_with_tools = llm.bind_tools(tools=tools)
    llm_chain = template | llm_with_tools
    graph = StateGraph(State)

    # preparing the nodes
    def llm_node(state: State):
        return {"messages": [llm_chain.invoke(state["messages"])]}

    tool_node = ToolNode(tools=tools)

    graph.add_node("llm", llm_node)
    graph.add_node("tools", tool_node)
    graph.add_node("toolcall_checker", forward)

    graph.add_edge(START, "llm")
    graph.add_conditional_edges(
        "llm", tool_call_attempted, {"toolcall_checker": "toolcall_checker", END: END}
    )
    graph.add_conditional_edges(
        "toolcall_checker", valid_toolcall, {"tools": "tools", "llm": "llm"}
    )
    graph.add_edge("tools", "llm")

    mem = MemorySaver()
    return graph.compile(checkpointer=mem)


def tool_call_attempted(state: State):

    if state["messages"] != []:
        ai_message = state["messages"][-1]
        content = ai_message.content
        tool_calls = ai_message.tool_calls
    else:
        raise ValueError(
            f"No messages found in input state to check for tool calls in."
        )

    # no tool_calls returned, but looks like it tried to
    if tool_calls or any(
        substr in content for substr in ("{", "}", "tool_call", "arguments")
    ):  
        return "toolcall_checker"
    else:
        return END
def valid_toolcall(state: State):

    if state["messages"] != []:
        ai_message = state["messages"][-1]
        content = ai_message.content
        tool_calls = ai_message.tool_calls
    else:
        raise ValueError(
            f"No messages found in input state to check for tool calls in."
        )
    
    if not tool_calls and any(
        substr in content for substr in ("{", "}", "tool_call", "arguments", "<tool")
    ):
        error_message = ToolMessage(
            tool_call_id="retry",
            content="Error: Your tool call was malformed or non-JSON. Please fix and retry.",
            invalid=True,
        )

        if "messages" not in state:
            state["messages"] = []
        state["messages"].append(error_message)

        return "llm"
    else:
        return "tools"
def forward(state: State):
    return {}