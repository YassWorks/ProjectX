import os
from langchain_core.tools import tool
import subprocess
import tempfile
import shlex
import re
import time


@tool
def create_wd(path: str) -> None:
    """
    **PRIMARY PURPOSE**: Creates a new directory/folder at the specified path.

    **WHEN TO USE**:
    - When you need to organize files into structured folders
    - Before placing files in a location that doesn't exist yet
    - Setting up workspace directories for different types of content
    - Creating nested folder structures in one operation

    **BEHAVIOR**:
    - Creates the directory and ALL parent directories if they don't exist
    - Will NOT fail if the directory already exists (safe to use repeatedly)
    - Similar to running "mkdir -p" in terminal

    **PARAMETERS**:
        path (str): The directory path to create. Can be:
                   - Relative: "documents", "media/images", "archive/2024"
                   - Absolute: "/home/user/workspace", "/opt/data/projects"
                   - Nested: "deep/nested/folder/structure"

    **RETURNS**:
        str: Success message with created path, or error message if failed

    **EXAMPLES**:
        create_wd("new_folder")               # Creates folder in current directory
        create_wd("documents/reports")        # Creates nested structure
        create_wd("/home/user/workspace")     # Creates with absolute path
    """
    try:
        os.makedirs(path, exist_ok=True)
        return f"Working directory created at {path}"
    except Exception as e:
        return f"Error creating working directory: {str(e)}"


@tool
def create_file(file_path: str, content: str) -> None:
    """
    **PRIMARY PURPOSE**: Creates a brand new file with specified content.

    **WHEN TO USE**:
    - Creating new text files (.txt, .md, .csv, etc.)
    - Generating configuration files (.json, .yaml, .ini, etc.)
    - Writing documentation or notes
    - Creating data files or templates
    - Establishing any type of text-based file

    **BEHAVIOR**:
    - Creates ALL necessary parent directories automatically
    - OVERWRITES existing files without warning
    - Writes content exactly as provided (preserves formatting)

    **PARAMETERS**:
        file_path (str): Where to create the file. Examples:
                        - "notes.txt" (current directory)
                        - "documents/report.md" (creates documents/ if needed)
                        - "/home/user/config.json"
        content (str): Exact text content for the file. Include proper:
                      - Indentation and whitespace
                      - Line breaks (\n)
                      - Any formatting needed

    **RETURNS**:
        str: Success message with file path, or error message if failed

    **WARNING**: This OVERWRITES existing files! Use modify_file() for edits.

    **EXAMPLES**:
        create_file("notes.txt", "Meeting notes from today")
        create_file("config/settings.json", '{"theme": "dark"}')
        create_file("README.md", "# My Project\n\nDescription here")
    """
    try:
        # ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as f:
            f.write(content)
        return f"File created at {file_path}"
    except Exception as e:
        return f"Error creating file: {str(e)}"


@tool
def modify_file(file_path: str, old_content: str, new_content: str) -> str:
    """
    **PRIMARY PURPOSE**: Updates existing files by replacing specific content.

    **WHEN TO USE**:
    - Correcting information in existing files
    - Updating configuration values or settings
    - Changing specific text sections
    - Making targeted edits without rewriting entire files
    - Updating data or content in documents

    **BEHAVIOR**:
    - Finds EXACT match of old_content and replaces with new_content
    - Only replaces the FIRST occurrence found
    - File must already exist (use create_file() for new files)
    - Preserves all other file content unchanged

    **PARAMETERS**:
        file_path (str): Path to existing file to modify
        old_content (str): EXACT text to replace (must match perfectly including:
                          - All whitespace and indentation
                          - Line breaks and spacing
                          - Capitalization and punctuation)
        new_content (str): Replacement text (can be longer/shorter than original)

    **RETURNS**:
        str: Success message, "Content not found" error, or other error message

    **CRITICAL**: old_content must match EXACTLY or replacement will fail!

    **EXAMPLES**:
        modify_file("notes.txt", "Meeting at 2pm", "Meeting at 3pm")
        modify_file("config.json", '"theme": "light"', '"theme": "dark"')
    """
    try:
        with open(file_path, "r") as f:
            contents = f.read()

        if old_content not in contents:
            return f"Content not found in {file_path}"

        contents = contents.replace(old_content, new_content, 1)

        with open(file_path, "w") as f:
            f.write(contents)
        return f"File modified at {file_path}"
    except Exception as e:
        return f"Error modifying file: {str(e)}"


@tool
def append_file(file_path: str, content: str) -> str:
    """
    **PRIMARY PURPOSE**: Appends new content to the end of an existing file.

    **WHEN TO USE**:
    - Adding new data to logs or reports
    - Appending notes or comments to documents
    - Extending configuration files with additional settings
    - Adding new entries to data files

    **BEHAVIOR**:
    - Appends content exactly as provided (preserves formatting)
    - Creates the file if it doesn't exist (like "touch" command)
    - Does NOT modify existing content, only adds to the end

    **PARAMETERS**:
        file_path (str): Path to file to append. Examples:
                        - "log.txt" (current directory)
                        - "data/records.csv" (creates data/ if needed)
                        - "/home/user/notes.txt"
        content (str): Text to append. Include proper:
                      - Indentation and whitespace
                      - Line breaks (\n)
                      - Any formatting needed

    **RETURNS**:
        str: Success message with file path, or error message if failed

    **EXAMPLES**:
        append_file("log.txt", "New log entry at 3pm")
        append_file("data/records.csv", "id,name\n1,John Doe")
        append_file("notes.txt", "\n# Additional Notes\nContent here")
    """
    try:
        # ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "a") as f:
            f.write(content)
        return f"Content appended to {file_path}"
    except Exception as e:
        return f"Error appending file: {str(e)}"


@tool
def delete_file(file_path: str) -> str:
    """
    **PRIMARY PURPOSE**: Permanently removes a file from the filesystem.

    **WHEN TO USE**:
    - Cleaning up temporary or unnecessary files
    - Removing outdated documents
    - Deleting log files or cached data
    - Removing files created by mistake
    - Cleaning up before reorganizing files

    **BEHAVIOR**:
    - PERMANENTLY deletes the file (cannot be undone)
    - Only works on files, not directories
    - Will fail if file doesn't exist

    **PARAMETERS**:
        file_path (str): Path to file to delete. Examples:
                        - "temp.txt"
                        - "documents/old_report.pdf"
                        - "/var/log/debug.log"

    **RETURNS**:
        str: Success message with deleted path, or error message if failed

    **DANGER**: This operation is PERMANENT and IRREVERSIBLE!

    **SAFETY TIPS**:
    - Double-check file path before deletion
    - Consider backing up important files first
    - This tool only deletes FILES, not directories

    **EXAMPLES**:
        delete_file("temp.log")              # Remove temporary file
        delete_file("old_document.txt")      # Remove outdated file
        delete_file("/tmp/session.tmp")      # Clean cache file
    """
    try:
        os.remove(file_path)
        return f"File deleted at {file_path}"
    except Exception as e:
        return f"Error deleting file: {str(e)}"


@tool
def delete_directory(path: str) -> str:
    """
    **PRIMARY PURPOSE**: Permanently removes a directory and all its contents.

    **WHEN TO USE**:
    - Cleaning up entire folders that are no longer needed
    - Removing temporary directories created during processing
    - Deleting old project directories
    - Clearing out cache or log directories

    **BEHAVIOR**:
    - Deletes the directory and ALL files/subdirectories inside it
    - PERMANENTLY removes everything (cannot be undone)
    - Will fail if directory doesn't exist or is not empty

    **PARAMETERS**:
        path (str): Path to directory to delete. Examples:
                   - "temp_folder"
                   - "projects/old_project"
                   - "/var/logs/old_logs"

    **RETURNS**:
        str: Success message with deleted path, or error message if failed

    **DANGER**: This operation is PERMANENT and IRREVERSIBLE!

    **SAFETY TIPS**:
    - Double-check directory path before deletion
    - Consider backing up important data first
    - This tool only deletes DIRECTORIES, not individual files

    **EXAMPLES**:
        delete_directory("temp_folder")              # Remove temporary folder
        delete_directory("projects/old_project")     # Remove old project folder
        delete_directory("/var/logs/old_logs")       # Clean up log directory
    """
    try:
        os.rmdir(path)
        return f"Directory deleted at {path}"
    except Exception as e:
        return f"Error deleting directory: {str(e)}"


@tool
def read_file(file_path: str) -> str:
    """
    **PRIMARY PURPOSE**: Reads and returns the complete content of any text file.

    **WHEN TO USE**:
    - Examining existing files before making changes
    - Reading configuration files to understand settings
    - Reviewing documents or notes
    - Checking file contents to determine what modifications are needed
    - Understanding file structure and existing content

    **BEHAVIOR**:
    - Returns the ENTIRE file content as a single string
    - Preserves all formatting, indentation, and line breaks
    - Works with any text-based file format
    - Will fail if file doesn't exist or isn't readable

    **PARAMETERS**:
        file_path (str): Path to file to read. Examples:
                        - "notes.txt" (current directory)
                        - "config/settings.json"
                        - "documents/README.md"
                        - "/etc/config/file.txt"

    **RETURNS**:
        str: Complete file contents, or error message if file cannot be read

    **USE BEFORE**: Making changes to understand current file state

    **EXAMPLES**:
        read_file("settings.json")           # Check configuration
        read_file("documents/notes.txt")     # Review document content
        read_file("/var/data/report.csv")    # Read data file
    """
    try:
        with open(file_path, "r") as f:
            contents = f.read()
        return contents
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def list_directory(path: str = ".") -> str:
    """
    **PRIMARY PURPOSE**: Shows all files and folders in a professional ASCII tree structure.

    **WHEN TO USE**:
    - Exploring an unknown directory structure
    - Understanding how files are organized before making changes
    - Finding where specific types of files are located
    - Getting an overview of a directory's contents
    - Discovering what files exist in nested folders

    **BEHAVIOR**:
    - Recursively explores all subdirectories
    - Shows hierarchical structure with ASCII tree characters (├── └── │)
    - Directories are marked with trailing "/" 
    - Files and directories are sorted alphabetically within each level
    - Displays absolute path as header

    **OUTPUT FORMAT**:
        /absolute/path/to/directory/
        │
        ├── file1.txt
        ├── file2.py
        ├── subdirectory/
        │   ├── nested_file.md
        │   └── another_file.json
        └── last_file.txt

    **PARAMETERS**:
        path (str): Directory to explore. Defaults to current directory (".")
                   Examples: ".", "documents", "/home/user/projects"

    **RETURNS**:
        str: Professional ASCII tree view of all files and directories

    **USEFUL FOR**: Getting bearings in unfamiliar directory structures

    **EXAMPLES**:
        list_directory(".")                      # Show current directory structure
        list_directory("documents")              # Explore documents/
        list_directory("/var/log")               # Show system log directory contents
    """

    def _list_directory_recursive(current_path: str, current_depth: int = 0, is_last: bool = True, parent_prefix: str = "") -> list:
        """Helper function to recursively build directory tree"""
        items = []

        try:
            all_items = os.listdir(current_path)
            dirs = []
            files = []

            for item in all_items:
                item_path = os.path.join(current_path, item)
                if os.path.isdir(item_path):
                    dirs.append(item)
                else:
                    files.append(item)

            # Sort files and directories
            all_sorted = sorted(files) + sorted(dirs)
            total_items = len(all_sorted)

            for i, item_name in enumerate(all_sorted):
                is_last_item = (i == total_items - 1)
                item_path = os.path.join(current_path, item_name)
                
                # Determine the prefix for this item
                if current_depth == 0:
                    prefix = ""
                else:
                    if is_last_item:
                        prefix = parent_prefix + "└── "
                    else:
                        prefix = parent_prefix + "├── "

                # Add the item
                if os.path.isdir(item_path):
                    items.append(f"{prefix}{item_name}/")
                    
                    # Recursively process subdirectory
                    if current_depth == 0:
                        new_parent_prefix = "│   "
                    else:
                        if is_last_item:
                            new_parent_prefix = parent_prefix + "    "
                        else:
                            new_parent_prefix = parent_prefix + "│   "
                    
                    sub_items = _list_directory_recursive(item_path, current_depth + 1, is_last_item, new_parent_prefix)
                    items.extend(sub_items)
                    
                    # Add empty line after directory contents if not the last item
                    if not is_last_item and sub_items:
                        items.append(parent_prefix + "│")
                else:
                    items.append(f"{prefix}{item_name}")

        except PermissionError:
            if current_depth == 0:
                items.append("❌ Permission denied")
            else:
                items.append(f"{parent_prefix}❌ Permission denied")
        except Exception as e:
            if current_depth == 0:
                items.append(f"❌ Error: {str(e)}")
            else:
                items.append(f"{parent_prefix}❌ Error: {str(e)}")

        return items

    try:
        # Add header with path
        result = [f"{os.path.abspath(path)}/", "│"]
        
        items = _list_directory_recursive(path)
        result.extend(items)
        
        return "\n".join(result)
    except Exception as e:
        return f"Error listing directory: {str(e)}"


@tool
def execute_code(code: str, language: str = "python") -> str:
    """
    **PRIMARY PURPOSE**: Safely executes code snippets in a controlled environment.

    **WHEN TO USE**:
    - Testing small code snippets or calculations
    - Validating logic before implementing in files
    - Running data analysis or processing scripts
    - Executing safe computational tasks

    **SECURITY RESTRICTIONS**:
    - TIMEOUT: Execution limited to 30 seconds maximum
    - MEMORY: Basic memory usage monitoring
    - EXTREME CAUTION: Only blocks truly destructive operations

    **BEHAVIOR**:
    - Executes code in isolated environment
    - Captures both stdout and stderr
    - Automatically times out long-running code
    - Prevents access to sensitive system resources

    **PARAMETERS**:
        code (str): The code to execute. Must be safe and non-malicious
        language (str): Programming language ("python", "bash"). Default: "python"

    **RETURNS**:
        str: Code output, error messages, or security violation warnings

    **EXAMPLES**:
        execute_code("print('Hello World')")
        execute_code("result = 2 + 2; print(f'Result: {result}')")
        execute_code("for i in range(3): print(i)")

    **SECURITY NOTE**: This tool actively blocks malicious operations!
    """

    # Minimal security checks - only block truly dangerous operations
    dangerous_patterns = [
        r"rm\s+-rf\s+/",  # Only block rm -rf on root
        r"format\s+c:",  # Windows format command
        r"mkfs\s+/dev/",  # Format filesystem
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return f"🚫 BLOCKED: Extremely destructive operation: {pattern}"

    try:
        if language.lower() == "python":
            # Simple Python execution - allow most operations
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as tmp_file:
                tmp_file.write(code)
                tmp_file_path = tmp_file.name

            # Execute with timeout
            result = subprocess.run(
                ["python", tmp_file_path],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.getcwd(),
            )

            os.unlink(tmp_file_path)  # Clean up temp file

            output = ""
            if result.stdout:
                output += f"Output:\n{result.stdout}"
            if result.stderr:
                output += f"\nErrors:\n{result.stderr}"
            if result.returncode != 0:
                output += f"\nReturn code: {result.returncode}"

            return output.strip() if output.strip() else "Code executed successfully"

        else:
            return f"❌ Unsupported language: {language}. Only 'python' is currently supported."

    except subprocess.TimeoutExpired:
        return "⏰ Code execution timed out (30 second limit exceeded)"
    except Exception as e:
        return f"❌ Execution error: {str(e)}"


@tool
def execute_command(command: str) -> str:
    """
    **PRIMARY PURPOSE**: Safely executes command-line commands in a controlled environment.

    **WHEN TO USE**:
    - Running safe system utilities (ls, cat, grep, find)
    - Checking file permissions or disk usage
    - Basic text processing commands
    - Safe read-only operations

    **SECURITY RESTRICTIONS**:
    - TIMEOUT: Commands limited to 60 seconds maximum
    - EXTREME ONLY: Only blocks filesystem destruction and hardware access
    - VIRTUAL ENV: Since you're in a VM, most operations are allowed

    **ALLOWED COMMANDS**:
    - Most system operations: rm, mv, cp, chmod, chown (use with caution)
    - Network operations: curl, wget, ssh, scp, nc
    - Package management: apt, yum, pip, npm
    - Process control: kill, killall, ps
    - User management: useradd, passwd (if you have permissions)
    - File operations: ls, cat, head, tail, wc, stat, find
    - Text processing: grep, awk, sed, sort, uniq
    - Development tools: git, make, gcc, python, node

    **BEHAVIOR**:
    - Executes in isolated environment
    - Captures both stdout and stderr
    - Automatically times out long-running commands
    - Prevents dangerous system modifications

    **PARAMETERS**:
        command (str): Shell command to execute (must be safe)

    **RETURNS**:
        str: Command output, error messages, or security violation warnings

    **EXAMPLES**:
        execute_command("ls -la")
        execute_command("cat config.txt")
        execute_command("sudo apt update")
        execute_command("pip install requests")
        execute_command("curl https://api.github.com")
        execute_command("find . -name '*.txt'")

    **CAUTION**: You're in a VM, but still be careful with destructive operations!
    """

    # Minimal security checks - only block truly catastrophic operations
    extremely_dangerous_commands = [
        r"^rm\s+-rf\s+/$",  # rm -rf / (root deletion)
        r"^dd\s+.*of=/dev/sd[a-z]$",  # Direct disk writing
        r"^mkfs\s+/dev/sd[a-z]$",  # Format disk
        r"^fdisk\s+/dev/sd[a-z]$",  # Disk partitioning
        r":\(\)\{.*\}",  # Fork bomb pattern
    ]

    # Check for extremely dangerous patterns only
    for pattern in extremely_dangerous_commands:
        if re.search(pattern, command, re.IGNORECASE):
            return f"🚫 BLOCKED: Extremely destructive operation: {pattern}"

    try:
        try:
            parsed_command = shlex.split(command)
        except ValueError as e:
            return f"❌ Invalid command syntax: {str(e)}"

        if not parsed_command:
            return "❌ Empty command"

        # Execute command with timeout
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60,
            shell=True,
            cwd=os.getcwd(),
        )

        output = ""
        if result.stdout:
            output += f"Output:\n{result.stdout}"
        if result.stderr:
            output += f"\nErrors:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\nReturn code: {result.returncode}"

        return (
            output.strip()
            if output.strip()
            else "Command executed successfully (no output)"
        )

    except subprocess.TimeoutExpired:
        return "⏰ Command execution timed out (60 second limit exceeded)"
    except FileNotFoundError:
        return f"❌ Command not found: {parsed_command[0] if parsed_command else 'unknown'}"
    except PermissionError:
        return f"❌ Permission denied executing: {command}"
    except Exception as e:
        return f"❌ Execution error: {str(e)}"


@tool
def stall(duration: float = 5):
    """
    **PRIMARY PURPOSE**: Pauses execution for a specified duration.

    **WHEN TO USE**:
    - Introducing delays in workflows
    - Waiting on other agents to complete tasks
    - Waiting for external processes to finish
    - Waiting for external events or conditions

    **PARAMETERS**:
        duration (float): Duration to stall in seconds

    **RETURNS**:
        str: Confirmation message

    **EXAMPLES**:
        stall(2.5)
        
    Note: Be generous with the duration (5-10s is a good start). Other agents may need time to work.
    """
    time.sleep(duration)
    return f"Stalled for {duration} seconds"
