import os
import json
import random
import datetime
import shutil
import asyncio
from agents.planner import PlannerAgent
from agents.coder import CoderAgent
from agents.model_api import model_client

def modify_code(workspace=None, request=None):
    """
    Modify the code based on the provided plan.
    """
    assert workspace is not None, "Workspace must be provided."
    assert request is not None, "Request must be provided."

    async def workflow():
        # Prepare workspace and copy codebase if needed
        if not os.path.exists(workspace):
            os.makedirs(workspace, exist_ok=True)

        planner_agent = PlannerAgent(
            name="planner",
            model_client=model_client,
            tools=[],
            reflect_on_tool_use=True,
            workspace=workspace,
        )
        coder_agent = CoderAgent(
            name="coder",
            model_client=model_client,
            tools=[],
            reflect_on_tool_use=True,
            workspace=workspace,
        )

        mission_goal = str(request)
        logs = []
        logs.append(await planner_agent.run(mission_goal, stream_output=False))
        logs.append(await coder_agent.run(mission_goal, stream_output=False))
        with open(os.path.join(workspace, 'logs.json'), 'w') as f:
            json.dump(logs, f, indent=4)
        print(f"执行任务 '{mission_goal}' 完成，工作空间: {workspace}")
        print(f"任务日志: {logs}")
        await model_client.close()

    asyncio.run(workflow())

