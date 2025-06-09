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

        log_dir = 'ca_logs'
        planner_agent = PlannerAgent(
            name="planner",
            model_client=model_client,
            tools=[],
            reflect_on_tool_use=True,
            workspace=workspace,
            log_dir=log_dir,
        )
        coder_agent = CoderAgent(
            name="coder",
            model_client=model_client,
            tools=[],
            reflect_on_tool_use=True,
            workspace=workspace,
            log_dir=log_dir,
        )

        mission_goal = str(request)
        logs = []
        logs.append(await planner_agent.run(mission_goal, stream_output=True))
        logs.append(await coder_agent.run(mission_goal, stream_output=True))
        with open(os.path.join(workspace, log_dir, 'logs.json'), 'w') as f:
            json.dump(logs, f, indent=4)
        await model_client.close()

    asyncio.run(workflow())

