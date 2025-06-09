from autogen_agentchat.agents import AssistantAgent
import os
from .common_agents import FileSystemAgent
from .utils import print_colored
import json
from autogen_agentchat.ui import Console

class PlannerAgent(AssistantAgent):
    def __init__(self, name, model_client, tools, reflect_on_tool_use=True, workspace='./executions/test/', log_dir='zeropde-core'):
        super().__init__(
            name=name, model_client=model_client, tools=tools, reflect_on_tool_use=reflect_on_tool_use)
        """
        1. Read the file structure of the code directory under workspace.
        2. Make a step-by-step plan to achieve the mission goal, specifying which files to read/modify/create.
        3. Write the plan to a file named 'plan.json' under the workspace directory.
        """
        self.workspace = workspace
        self.log_dir = log_dir
        self.step1_prompt = f"""
            The mission goal is: MISSION_GOAL
            The file structure of the project is: FILE_STRUCTURE
            Based on the file structure, identify the most relevant files and directories to achieve the mission goal.
            List these as a JSON array of relative paths.
            """
        self.list_dir_agent = FileSystemAgent(
            name="list_dir_agent",
            model_client=model_client,
            workspace=workspace,
            system_message=f"""
            Given a message specifying files or directories, list their directory trees in JSON format.
            The root code directory is {self.workspace}.
            """
        )
        self.step2_prompt = f"""
            The mission goal is: MISSION_GOAL
            The file structure is: FILE_STRUCTURE
            The relevant files and directories are: RELEVANT_PATHS
            Now, make a step-by-step plan to achieve the mission goal.
            Each step should specify:
                - files to read first ("dependencies": list)
                - how to modify or implement code ("modification": string)
                - where to save the modified code ("save_path": string)
                - any extra info ("extra_info": dict)
                - step number ("step": int, starting from 1)
            Output the plan as:
            ```json
            {{
                "plan": [
                    {{
                        "dependencies": ["relative/path1", ...],
                        "modification": "Describe the code change.",
                        "save_path": "relative/path/to/save.py",
                        "extra_info": {{}},
                        "step": 1
                    }},
                    ...
                ]
            }}
            ```
            """
        self.save_file_prompt = f"""
            Write a file named 'plan.json' under the workspace directory {self.workspace} according to the following message: PLAN_MESSAGE
            """
        self.save_plan_agent = FileSystemAgent(
            name="filesys_agent",
            model_client=model_client,
            workspace=workspace,
            system_message="""Save files as requested. Use the correct function provided in workbench."""
        )

    async def run(self, mission_goal, stream_output=False):
        # Step 1: Read file structure
        code_root = os.path.join(self.workspace, self.log_dir)
        file_structure = []
        for root, dirs, files in os.walk(code_root):
            rel_root = os.path.relpath(root, code_root)
            for d in dirs:
                file_structure.append(os.path.join(rel_root, d) if rel_root != '.' else d)
            for f in files:
                file_structure.append(os.path.join(rel_root, f) if rel_root != '.' else f)
        file_structure_str = json.dumps(file_structure, indent=2)

        print_colored("[Planner] Working on the mission goal:", "blue")
        print_colored(mission_goal, "green")
        print_colored("[Planner] Step 1: Identifying relevant files and directories...", "yellow")
        step1_prompt = self.step1_prompt.replace("MISSION_GOAL", mission_goal).replace("FILE_STRUCTURE", file_structure_str)
        relevant_paths_response = await Console(self.run_stream(task=step1_prompt)) if stream_output else await super().run(task=step1_prompt)

        print_colored("[Planner] Step 2: Making a step-by-step plan...", "yellow")
        relevant_paths = relevant_paths_response.messages[-1].content
        step2_prompt = self.step2_prompt.replace("MISSION_GOAL", mission_goal).replace("FILE_STRUCTURE", file_structure_str).replace("RELEVANT_PATHS", relevant_paths)
        plan_response = await Console(self.run_stream(task=step2_prompt)) if stream_output else await super().run(task=step2_prompt)

        print_colored(f"[Planner] Step 3: Writing plan to {os.path.join(self.workspace, 'plan.json')}", "yellow")
        save_file_prompt = self.save_file_prompt.replace("PLAN_MESSAGE", plan_response.messages[-1].content)
        save_file_response = await Console(self.save_plan_agent.run_stream(task=save_file_prompt)) if stream_output else await self.save_plan_agent.run(task=save_file_prompt)

        print_colored("[Planner] Planning finished", "green")
        return {
            "relevant_paths_response": relevant_paths_response.messages[-1].content,
            "plan_response": plan_response.messages[-1].content,
            "save_file_response": save_file_response.messages[-1].content
        }
