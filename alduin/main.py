"""Alduin - A minimal CLI coding agent."""

import os
from typing import Any

import anthropic
import dotenv
from rich.console import Console

from alduin import theme, ui, llm, system_prompt, schema_converter, tool



def execute_tool(console, name: str, tool_lookup, args: dict[str, Any]):
    ui.print_tool_request(console, name, args)

    # Find request function
    tool_fn = tool_lookup.get(name)


    if tool_fn is None:
        error = f"Error: Unknown tool '{name}'"
        ui.print_tool_error(console, error)
        return error


    try: 
        result = tool_fn(**args)
        ui.print_tool_result(console, name, result)
        return str(result)

    except  Exception as e:
        error = f"Error executing tool '{name}': '{e}'"
        ui.print_tool_error(console, error, name)
        return error


    

def agent_loop(client: anthropic.Anthropic, console: Console) -> None:
    """Run the main agent loop: read input, call LLM, execute tools, repeat.

    Args:
        client: The initialized Anthropic client.
        console: The Rich Console for logging and UI.
    """

    conversation: list[dict[str, Any]] = []

    active_tools = [tool.read_file]
    
    tool_lookup = {
        fn.__name__: fn
        for fn in active_tools    
    }
    
    tool_schemas = schema_converter.generate_tool_schema(active_tools)

    while True:
        try:
            user_input = input("🧑‍💻 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            ui.clear_previous_line()
            ui.print_goodbye(console)
            return

        if not user_input:
            continue

        conversation.append({"role": "user", "content": user_input})

        ui.clear_previous_line()
        ui.print_user_message(console, user_input)

        llm_response = llm.call(
            client=client,
            console=console,
            system_prompt=system_prompt.get(),    
            messages=conversation,         
            tool_schemas=tool_schemas,     
        )

        conversation.append({"role": "assistant", "content": llm_response.content})
        

        for block in llm_response.content:
            if block.type == "text":    
                ui.print_assistant_reply(
                    console=console,
                    text=block.text,           
                    input_tokens=llm_response.usage.input_tokens,
                    output_tokens=llm_response.usage.output_tokens
                )
            elif block.type == "tool_use":
                execute_tool(
                    console, 
                    block.name,
                    block.input
                )





def main() -> None:
    """Entry point for the Alduin CLI agent.

    Initializes console, checks API key, and starts the agent loop.
    """

    console = Console(theme=theme.ALDUIN_THEME)
    ui.print_banner(console)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        ui.print_error(console, "ANTHROPIC_API_KEY environment variable is not set.")
        return

    client = anthropic.Anthropic(api_key=api_key)
    agent_loop(client=client, console=console)


if __name__ == "__main__":
    dotenv.load_dotenv()
    main()
