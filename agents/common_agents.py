from autogen_agentchat.agents import AssistantAgent
from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams

class FileSystemAgent(AssistantAgent):
    def __init__(self, name, model_client, workspace='./executions/test/', system_message=None):
        filesys_mcp_server = StdioServerParams(
            command="npx",
            args=["@modelcontextprotocol/server-filesystem", workspace], read_timeout_seconds=60,
        )
        super().__init__(
            name=name,
            model_client=model_client,
            workbench=McpWorkbench(filesys_mcp_server),
            reflect_on_tool_use=True,
            system_message=system_message or """Save files as requested. Use the correct function provided in workbench."""
        )
        self.workspace = workspace

    async def run(self, task):
        return await super().run(task=task)