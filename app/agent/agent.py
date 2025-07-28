from app.agent.config.config import get_agent
from app.utils.ascii_art import ASCII_ART
import uuid
from rich.console import Console
from rich.text import Text
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.table import Table
import time
import os
from langchain_core.messages import AIMessage, ToolMessage


class Agent:

    def __init__(self, model_name, api_key, system_prompt=None):
        self.model_name = model_name
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.agent = get_agent(
            model_name=model_name, api_key=api_key, system_prompt=system_prompt
        )
        self.console = Console()

    def _print_welcome(self):
        """Print a beautiful welcome screen"""
        # Create gradient ASCII art
        ascii_text = Text(ASCII_ART)
        ascii_text.stylize("bold magenta", 0, len(ASCII_ART))

        self.console.print()
        self.console.print(ascii_text)
        self.console.print()

        # Instructions
        self.console.print("[bold yellow]📋 Instructions[/bold yellow]")
        self.console.print("━" * 50, style="yellow")
        self.console.print(
            "💬  Type your message and press Enter to chat", style="white"
        )
        self.console.print(
            "🚪  Type 'quit', 'exit', or 'q' to end the conversation", style="white"
        )
        self.console.print(
            "🧹  Type 'clear' to clear conversation history", style="white"
        )
        self.console.print(
            "🖥️  Type 'cls', 'clearterm', or 'clearscreen' to clear terminal",
            style="white",
        )
        self.console.print(
            f"🎯  Current model: [bold green]{self.model_name}[/bold green]",
            style="white",
        )
        self.console.print("━" * 50, style="yellow")
        self.console.print()

    def _print_tool_call(self, tool_name, args):
        """Print tool call information in a beautiful format"""
        self.console.print()
        self.console.print(
            f"⚡ [bold yellow]Tool Called:[/bold yellow] [bold green]{tool_name}[/bold green]"
        )
        self.console.print("━" * 60, style="green")

        tool_table = Table(show_header=True, header_style="bold magenta", box=None)
        tool_table.add_column("Parameter", style="cyan", width=20)
        tool_table.add_column("Value", style="white")

        for k, v in args.items():
            value_str = str(v)
            if len(value_str) > 100:
                value_str = value_str[:97] + "..."
            tool_table.add_row(k, value_str)

        self.console.print(tool_table)
        self.console.print("━" * 60, style="green")
        self.console.print()

    def _print_tool_output(self, tool_message):
        """Print tool execution output in a beautiful format"""
        self.console.print()
        self.console.print(
            f"📤 [bold cyan]Tool Output:[/bold cyan] [bold green]{tool_message.name}[/bold green]"
        )
        self.console.print("━" * 60, style="cyan")
        
        # Clean up the output content
        output_content = tool_message.content.strip()
        if output_content.startswith("Output:\n"):
            output_content = output_content[8:]  # Remove "Output:\n" prefix
        
        self.console.print(output_content, style="white")
        self.console.print("━" * 60, style="cyan")
        self.console.print()

    def _print_user_message(self, message):
        """Print user message in a styled format"""
        self.console.print()
        self.console.print("👤 [bold blue]You[/bold blue]")
        self.console.print("─" * 40, style="blue")
        self.console.print(message, style="white")
        self.console.print("─" * 40, style="blue")
        self.console.print()

    def _print_ai_response(self, content):
        """Print AI response in a styled format"""
        # Try to parse as markdown if it looks like it contains code or formatting
        if "```" in content or "#" in content or "*" in content:
            try:
                ai_content = Markdown(content)
            except:
                ai_content = content
        else:
            ai_content = content

        self.console.print()
        self.console.print("🤖 [bold green]AI Assistant[/bold green]")
        self.console.print("─" * 50, style="green")
        self.console.print(ai_content)
        self.console.print("─" * 50, style="green")
        self.console.print()

    def _simulate_thinking(self):
        """Show a thinking animation"""
        with self.console.status("[bold green]🧠 AI is thinking...", spinner="dots"):
            time.sleep(0.5)  # Brief pause for effect

    def start_chat(self):
        """
        Start an isolated chat session with the code generation agent.
        During this session, you do not have access to the other agents.
        Arguments:
            message (str | None): Optional message for single-query sessions.
        """

        self._print_welcome()

        configuration = {
            "configurable": {"thread_id": "abc123"},
            "recursion_limit": 100,
        }

        while True:
            try:
                user_input = Prompt.ask(
                    "\n[bold blue]You[/bold blue]", console=self.console
                ).strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    self.console.print()
                    self.console.print("🚪 [yellow]Goodbye![/yellow]")
                    self.console.print("─" * 30, style="bright_blue")
                    self.console.print(
                        "[bold cyan]Thanks for using the AI Assistant! 👋[/bold cyan]"
                    )
                    self.console.print("─" * 30, style="bright_blue")
                    self.console.print()
                    break

                if user_input.lower() == "clear":
                    # new session
                    configuration["configurable"]["thread_id"] = str(uuid.uuid4())

                    self.console.print()
                    self.console.print("🧹 [yellow]History Cleared[/yellow]")
                    self.console.print("─" * 30, style="green")
                    self.console.print(
                        "[bold green]✨ Conversation history has been cleared![/bold green]"
                    )
                    self.console.print("─" * 30, style="green")
                    self.console.print()
                    continue

                if user_input.lower() in ["cls", "clearterm", "clearscreen"]:
                    os.system("clear")
                    continue

                if not user_input:
                    continue

                self._simulate_thinking()

                for chunk in self.agent.stream({"messages": user_input}, configuration):
                    
                    # Handle agent chunks (AI messages)
                    if "agent" in chunk:
                        agent_data = chunk["agent"]
                        if "messages" in agent_data:
                            messages = agent_data["messages"]
                            if messages and isinstance(messages[0], AIMessage):
                                ai_message = messages[0]
                                
                                # Print tool calls if present
                                if ai_message.tool_calls:
                                    for tool_call in ai_message.tool_calls:
                                        self._print_tool_call(
                                            tool_call["name"], tool_call["args"]
                                        )
                                
                                # Print AI response content (even if empty)
                                if ai_message.content and ai_message.content.strip():
                                    self._print_ai_response(ai_message.content)
                    
                    # Handle tools chunks (tool execution results)
                    elif "tools" in chunk:
                        tools_data = chunk["tools"]
                        if "messages" in tools_data:
                            for tool_message in tools_data["messages"]:
                                self._print_tool_output(tool_message)


            except KeyboardInterrupt:
                self.console.print()
                self.console.print("⚠️  [yellow]Session Interrupted[/yellow]")
                self.console.print("─" * 30, style="red")
                self.console.print("[bold red]Interrupted by user 🛑[/bold red]")
                self.console.print("─" * 30, style="red")

                self.console.print()
                self.console.print("🚪 [yellow]Goodbye![/yellow]")
                self.console.print("─" * 30, style="bright_blue")
                self.console.print(
                    "[bold cyan]Thanks for using the AI Assistant! 👋[/bold cyan]"
                )
                self.console.print("─" * 30, style="bright_blue")
                self.console.print()
                break
            except Exception as e:
                self.console.print()
                self.console.print("⚠️  [red]Error Occurred[/red]")
                self.console.print("─" * 40, style="red")
                self.console.print(f"[bold red]❌ Error: {str(e)}[/bold red]")
                self.console.print("[dim]Please try again...[/dim]")
                self.console.print("─" * 40, style="red")
                self.console.print()
                import traceback

                traceback.print_exc(file=self.console.file)
