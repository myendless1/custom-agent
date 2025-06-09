import sys
import os
import json
import argparse

def get_request_and_agent():
    """
    Parse user input or config to get the mission goal/request,
    select the custom agent/workflow to use, and collect extra args.
    """
    parser = argparse.ArgumentParser(description="Run custom agent workflow")
    parser.add_argument('--request', type=str, required=True, help='Mission goal or request')
    parser.add_argument('--agent', type=str, default='coder_custom', help='Custom agent/workflow to use')
    parser.add_argument('--workspace', type=str, default='./executions/test/', help='Workspace directory')
    # Add more arguments as needed

    args = parser.parse_args()
    request = args.request
    agent_name = args.agent
    extra_args = {"workspace": args.workspace}
    # Add more extra_args if needed

    return request, agent_name, extra_args

if __name__ == "__main__":
    request, agent_name, extra_args = get_request_and_agent()
    # Dynamically import and call the custom agent/workflow
    if agent_name == "coder_custom":
        from customs.coder_custom import modify_code
        workspace = extra_args.get("workspace", "./executions/test/")
        modify_code(workspace=workspace, request=request)
    else:
        raise NotImplementedError(f"Agent {agent_name} not implemented.")
