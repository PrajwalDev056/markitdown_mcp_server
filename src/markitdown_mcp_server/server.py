from os import listdir
from typing import Tuple
import json

import mcp.types as types
from markitdown import MarkItDown
from mcp.server import NotificationOptions, Server, models, stdio

PROMPTS = {
    "md": types.Prompt(
        name="md",
        description="Convert document to markdown format using MarkItDown",
        arguments=[
            types.PromptArgument(
                name="file_path",
                description="A URI to any document or file",
                required=True,
            )
        ],
    ),
    "md_lint": types.Prompt(
        name="md_lint",
        description="Convert document to markdown and apply markdownlint rules for quality",
        arguments=[
            types.PromptArgument(
                name="file_path",
                description="A URI to any document or file",
                required=True,
            ),
            types.PromptArgument(
                name="lint_rules",
                description="Comma-separated list of markdownlint rules to apply (e.g., 'MD010,MD018,MD041')",
                required=False,
            )
        ],
    ),
    "ls": types.Prompt(
        name="ls",
        description="list files in a directory",
        arguments=[
            types.PromptArgument(
                name="directory",
                description="directory to list files",
                required=True,
            )
        ],
    ),
}


def convert_to_markdown(file_path: str) -> Tuple[str | None, str]:
    try:
        md = MarkItDown()
        result = md.convert(file_path)
        return result.title, result.text_content

    except Exception as e:
        return None, f"Error converting document: {str(e)}"


def apply_markdownlint_rules(markdown_content: str, rules: str = None) -> Tuple[str, list]:
    """
    Apply markdownlint rules to markdown content.
    Returns (fixed_content, lint_errors)
    """
    try:
        # Import markdownlint dynamically to avoid dependency issues
        import subprocess
        import tempfile
        import os

        # Create temporary file with markdown content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(markdown_content)
            temp_file_path = temp_file.name

        try:
            # Run markdownlint with configuration file
            config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.markdownlint.json')
            cmd = ['markdownlint', temp_file_path, '--json']
            if os.path.exists(config_file):
                cmd.extend(['--config', config_file])
            elif rules:
                cmd.extend(['--config', json.dumps({'default': True, 'rules': {rule.strip(): True for rule in rules.split(',')}})])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            lint_errors = []
            if result.stdout:
                try:
                    lint_errors = json.loads(result.stdout)
                except json.JSONDecodeError:
                    lint_errors = [{"error": "Failed to parse lint output"}]

            # Apply fixes if possible
            fixed_content = markdown_content
            if lint_errors:
                # For now, return the original content with lint information
                # In a full implementation, you'd apply the fixes here
                pass

            return fixed_content, lint_errors

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        return markdown_content, [{"error": f"Linting failed: {str(e)}"}]


# Initialize server
app = Server("document-conversion-server")


@app.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    return list(PROMPTS.values())


@app.get_prompt()
async def get_prompt(
    name: str, arguments: dict[str, str] | None = None
) -> types.GetPromptResult:
    if name not in PROMPTS:
        raise ValueError(f"Prompt not found: {name}")

    if name == "md":
        if not arguments:
            raise ValueError("Arguments required")

        file_path = arguments.get("file_path")

        if not file_path:
            raise ValueError("file_path is required")

        try:
            markdown_title, markdown_content = convert_to_markdown(file_path)

            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=f"Here is the converted document in markdown format:\n{'' if not markdown_title else markdown_title}\n{markdown_content}",
                        ),
                    )
                ]
            )

        except Exception as e:
            raise ValueError(f"Error processing document: {str(e)}")

    elif name == "md_lint":
        if not arguments:
            raise ValueError("Arguments required")

        file_path = arguments.get("file_path")
        lint_rules = arguments.get("lint_rules", "MD010,MD018,MD041,MD013,MD033,MD040")

        if not file_path:
            raise ValueError("file_path is required")

        try:
            markdown_title, markdown_content = convert_to_markdown(file_path)

            if markdown_content:
                # Apply markdownlint rules
                fixed_content, lint_errors = apply_markdownlint_rules(markdown_content, lint_rules)

                # Format the output
                output = f"# Converted Document with Markdownlint Quality Check\n\n"
                if markdown_title:
                    output += f"**Title:** {markdown_title}\n\n"

                output += f"**Applied Rules:** {lint_rules}\n\n"

                if lint_errors:
                    output += f"**Lint Issues Found:**\n"
                    for error in lint_errors:
                        if isinstance(error, dict):
                            if 'error' in error:
                                output += f"- {error['error']}\n"
                            else:
                                output += f"- Line {error.get('lineNumber', '?')}: {error.get('ruleDescription', 'Unknown rule')}\n"
                    output += f"\n"

                output += f"**Markdown Content:**\n{markdown_content}\n\n"

                if fixed_content != markdown_content:
                    output += f"**Fixed Content:**\n{fixed_content}\n"

                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=output,
                            ),
                        )
                    ]
                )
            else:
                raise ValueError("Failed to convert document to markdown")

        except Exception as e:
            raise ValueError(f"Error processing document with linting: {str(e)}")

    elif name == "ls":
        try:
            directory = arguments["directory"]
            files = listdir(directory)

            # Format the output in a structured, informative way
            file_count = len(files)
            formatted_output = f"Directory listing for: {directory}\n"
            formatted_output += f"Total files: {file_count}\n\n"

            # Group files by type if possible
            extensions = {}
            no_extension = []

            for file in files:
                if "." in file:
                    ext = file.split(".")[-1].lower()
                    if ext not in extensions:
                        extensions[ext] = []
                    extensions[ext].append(file)
                else:
                    no_extension.append(file)

            # Add file groupings to output
            if extensions:
                formatted_output += "Files by type:\n"
                for ext, files_of_type in extensions.items():
                    formatted_output += f"- {ext.upper()} files ({len(files_of_type)}): {', '.join(files_of_type)}\n"

            if no_extension:
                formatted_output += f"\nFiles without extension ({len(no_extension)}): {', '.join(no_extension)}\n"

            # Add complete listing
            formatted_output += "\nComplete file listing:\n"
            for idx, file in enumerate(sorted(files), 1):
                formatted_output += f"{idx}. {file}\n"

            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=formatted_output,
                        ),
                    )
                ]
            )
        except Exception as e:
            raise ValueError(f"Error listing directory: {str(e)}")
    raise ValueError("Prompt implementation not found")


async def run():
    async with stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            models.InitializationOptions(
                server_name="example",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
