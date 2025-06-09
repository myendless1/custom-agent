# CustomAgents

This project leverages [AutoGen](https://github.com/microsoft/autogen) and MCP (Multi-Agent Collaboration Platform) to help users accomplish complex tasks automatically and intelligently. By defining custom agents, the system can plan, code, and manage files or repositories in a smart, automated way.

## Features

- **Custom Agents**: Specialized agents for planning, coding, file system operations, and git operations.
- **Task Automation**: Automatically decomposes user goals into actionable steps and executes them.
- **Collaboration**: Agents collaborate to read, modify, and create code, manage files, and handle git repositories.
- **Extensible**: Easily add new agents or tools for additional capabilities.

## Main Agents

- **PlannerAgent**: Plans the steps needed to achieve a user-defined mission goal.
- **CoderAgent**: Implements code changes step-by-step according to the plan.
- **FileSystemAgent**: Handles file and directory operations.
- **GitAgent**: Performs common git operations (status, add, commit, push, pull, etc.).

## Usage

1. **Define your mission goal** (e.g., "Add a new feature to my project").
2. **Run the PlannerAgent** to generate a step-by-step plan.
3. **Run the CoderAgent** to execute the plan and modify code as needed.
4. **Use the GitAgent** to manage version control operations.

## Requirements

- Python 3.10+
- [AutoGen](https://github.com/microsoft/autogen)
- MCP (if required for your workflow)
- Other dependencies as specified in your environment

## Getting Started

1. Clone this repository.
2. Install dependencies.
3. Configure your model client and workspace.
4. Run the agents as needed for your workflow.

## Example

```python
# main.py
from main import planner, coder, git_agent

plan = await planner.run(mission_goal="Add a REST API endpoint.")
await coder.run(mission_goal="Add a REST API endpoint.")
git_agent.git_status()
```

## License

MIT License

## Acknowledgements

- [Microsoft AutoGen](https://github.com/microsoft/autogen)
- MCP and the open-source community
- [DeepSeek](https://github.com/deepseek-ai)
