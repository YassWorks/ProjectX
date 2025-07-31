from app.agent.config.config import get_agent
from langchain_core.messages import AIMessage
from app.utils.ascii_art import ASCII_ART
from app.agent.ui import AgentUI
from rich.console import Console
from rich.prompt import Prompt
import langgraph
import uuid
import os
import openai


class Agent:

    def __init__(self, model_name, api_key, system_prompt=None):
        self.model_name = model_name
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.agent = get_agent(
            model_name=model_name, api_key=api_key, system_prompt=system_prompt
        )
        self.console = Console()
        self.ui = AgentUI(self.console)

    def start_chat(self, recursion_limit: int = 100):

        self.ui.logo(ASCII_ART)
        self.ui.help(self.model_name)

        configuration = {
            "configurable": {"thread_id": "abc123"},
            "recursion_limit": recursion_limit,
        }

        while True:
            try:
                user_input = Prompt.ask(
                    "\n[bold blue]You[/bold blue]", console=self.console
                ).strip()

                if user_input.lower() in ["/quit", "/exit", "/q"]:
                    self.ui.goodbye()
                    break

                if user_input.lower() == "/clear":
                    # new session
                    configuration["configurable"]["thread_id"] = str(uuid.uuid4())
                    self.ui.history_cleared()
                    continue

                if user_input.lower() in ["/cls", "/clearterm", "/clearscreen"]:
                    os.system("clear")
                    continue

                if user_input.lower() in ["/help", "/h"]:
                    self.ui.help(self.model_name)
                    continue
                
                if len(user_input.lower()) > 0 and user_input.lower()[0] == "/":
                    self.ui.error("Unknown command. Type /help for instructions.")
                    continue

                if user_input.lower() == "/model":
                    self.ui.status_message(
                        title="Current Model",
                        message=self.model_name,
                    )
                    continue

                if not user_input:
                    continue

                command_parts = user_input.lower().split()
                
                if command_parts[0] == "/model":
                    if len(command_parts) > 1 and command_parts[1] == "change":
                        if len(command_parts) > 2:
                            new_model = command_parts[2]
                            self.ui.status_message(
                                title="Change Model",
                                message=f"Changing model to {new_model}",
                            )
                            self.model_name = new_model
                            self.agent = get_agent(
                                model_name=self.model_name,
                                api_key=self.api_key,
                                system_prompt=self.system_prompt,
                            )
                            continue
                        else:
                            self.ui.error("Please specify a model to change to.")
                            continue
                    else:
                        self.ui.error("Unknown command. Type /help for instructions.")
                        continue

                self.ui.simulate_thinking()

                # start response streaming
                for chunk in self.agent.stream(
                    {"messages": [("human", user_input)]}, configuration
                ):

                    if "llm" in chunk:
                        llm_data = chunk["llm"]
                        if "messages" in llm_data:
                            messages = llm_data["messages"]
                            if messages and isinstance(messages[0], AIMessage):
                                ai_message = messages[0]

                                if ai_message.tool_calls:
                                    for tool_call in ai_message.tool_calls:
                                        self.ui.tool_call(
                                            tool_call["name"], tool_call["args"]
                                        )

                                if ai_message.content and ai_message.content.strip():
                                    self.ui.ai_response(ai_message.content)

                    elif "tools" in chunk:
                        tools_data = chunk["tools"]
                        if "messages" in tools_data:
                            for tool_message in tools_data["messages"]:
                                self.ui.tool_output(
                                    tool_message.name, tool_message.content
                                )

            except KeyboardInterrupt:
                self.ui.session_interrupted()
                self.ui.goodbye()
                break
            except langgraph.errors.GraphRecursionError as e:
                self.ui.recursion_warning()
                ######## placeholder for continuing logic
            except openai.RateLimitError:
                self.ui.status_message(
                    "⏳",
                    title="Rate Limit Exceeded",
                    message="Please try again later or switch to a different model.",
                    style="red",
                )
            except Exception as e:
                self.ui.error(str(e))
                self.ui.dev_traceback()  # dev (remove later)
