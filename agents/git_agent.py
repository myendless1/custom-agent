import subprocess
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from model_api import model_client  # Assuming model_client is defined in model_api.py
import asyncio

def run_git_command(args: list[str], cwd: str = ".") -> dict:
    """Run a git command and return output or error."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return {"success": True, "output": result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": e.stderr.strip()}

# Define common git command tools
def git_status(cwd: str = ".") -> dict:
    """Get git status."""
    return run_git_command(["status"], cwd)

def git_add(files: list[str] | str, cwd: str = ".") -> dict:
    """Add files to staging area."""
    if isinstance(files, str):
        files = [files]
    return run_git_command(["add"] + files, cwd)

def git_commit(message: str, cwd: str = ".") -> dict:
    """Commit staged changes."""
    return run_git_command(["commit", "-m", message], cwd)

def git_push(remote: str = "origin", branch: str = "main", cwd: str = ".") -> dict:
    """Push commits to remote."""
    return run_git_command(["push", remote, branch], cwd)

def git_pull(remote: str = "origin", branch: str = "main", cwd: str = ".") -> dict:
    """Pull latest changes from remote."""
    return run_git_command(["pull", remote, branch], cwd)

def git_checkout(branch: str, cwd: str = ".") -> dict:
    """Checkout a branch."""
    return run_git_command(["checkout", branch], cwd)

def git_branch(branch: str = None, cwd: str = ".") -> dict:
    """List or create branch."""
    if branch:
        return run_git_command(["checkout", "-b", branch], cwd)
    else:
        return run_git_command(["branch"], cwd)

def git_log(n: int = 5, cwd: str = ".") -> dict:
    """Show last n commits."""
    return run_git_command(["log", f"-{n}", "--oneline"], cwd)

# Tool registry for the agent
GIT_TOOLS = [
    git_status,
    git_add,
    git_commit,
    git_push,
    git_pull,
    git_checkout,
    git_branch,
    git_log,
]

class GitAgent(AssistantAgent):
    def __init__(
        self,
        name: str,
        model_client,
        workspace: str = ".",
        tools: list = GIT_TOOLS,
        reflect_on_tool_use: bool = True
    ):
        super().__init__(
            name=name,
            model_client=model_client,
            tools=tools,
            reflect_on_tool_use=reflect_on_tool_use
        )
        self.workspace = workspace
        self.system_message = (
            "You are a GitAgent. You help users perform git operations such as status, add, commit, push, pull, "
            "checkout, branch, and log. Use the provided tools to execute git commands in the workspace."
        )
        self.prompt = """
        Please Help with TASK, the workspace is at WORKSPACE.
        """

if __name__ == "__main__":
    agent = GitAgent(name="git_agent", model_client=model_client, workspace=".")
    print(agent.system_message)
    response = Console(
        agent.run_stream(
            task="Check the git status and commit changes if any.",
        )
    )