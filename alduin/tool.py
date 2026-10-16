"""Module for tool implementations for the coding agent."""

from pathlib import Path


def read_file(path: str) -> str:
    """Read the contents of a file.

    Args:
        path: The path to the file to read.

    Returns:
        The contents of the file, or an error message if it fails.
    """

    file_path = Path(path)

    if not file_path.is_file():
        return f"Error: File not found: {path}"

    return file_path.read_text(encoding="utf-8")


def edit_file(path: str, old_str: str, new_str: str) -> str:
    """Create or edit a file by replacing occurrences of a string.

    This tool can be used to do both, create a new file (if old_str is empty) or edit an existing file.

    Args:
        path: The path to the file to edit.
        old_str: The string to be replaced.
        new_str: The replacement string.

    Returns:
        A success message, or an error message if it fails.
    """

    file_path = Path(path).resolve()

    if not file_path.is_relative_to(Path.cwd()):
        return "Error: path is outside the project foler"

    if old_str == "":
        if file_path.exists() and file_path.read_text(encoding="utf-8") != "":
            return f"Error: {path} already exists and is not empty"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(new_str, encoding="utf-8")
        return f"Created {path}"


    if not file_path.is_file():
        return f"Error: file not found: {path}"

    text = file_path.read_text(encoding="utf-8")
    count = text.count(old_str)
    if count == 0:
        return "Error: old_str not found in the file"
    if count > 1:
        return f"Error: old_str appears {count} times; give a more unique string"


    file_path.write_text(text.replace(old_str, new_str), encoding="utf-8")
    return f"Edited {path}"


def list_files(path: str) -> str:
    """List files in a directory.

    Args:
        path: The path to the directory to list files in.

    Returns:
        A newline-separated list of file names, or an error message.
    """

    p = Path(path)
    if not p.is_dir():
        return f"Error: not a directory: {path}"

    contents = sorted(p.iterdir())
    if not contents:
        return "Directory is empty."

    lines = [f"{item.name}/" if item.is_dir() else item.name for item in contents]
    return "\n".join(lines)


def bash(command: str) -> str:
    """Execute a bash command and return its output.

    Ask the user for confirmation before executing, and handle errors gracefully.

    Args:
        command: The bash command to execute.

    Returns:
        The output of the command, or an error message.
    """

    pass
